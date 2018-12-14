from . import db, avatars
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from datetime import datetime
import hashlib
from flask import request
from markdown import markdown
import bleach
from flask_avatars import Identicon
from . import photosSet
import os


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()
    
    
    def __repr__(self):
        return '<Role %r>' % self.name


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer,db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer,db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime,default=datetime.utcnow)
        
class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship('Post', backref='author', lazy='dynamic', cascade='all')
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade="all")
    replies = db.relationship('Reply', backref='author', primaryjoin='Reply.author_id==User.id')
    relpies_to = db.relationship('Reply', backref='replyto_user', primaryjoin='Reply.replyto_uid==User.id')
    messages = db.relationship('Message', backref='author', primaryjoin='Message.author_id==User.id', lazy='dynamic', cascade='all')
    own_messages = db.relationship('Message', backref='owner', primaryjoin='Message.user_id==User.id', lazy='dynamic', cascade='all')
    message_replies = db.relationship('MessageReply', backref='author', primaryjoin='MessageReply.author_id==User.id', lazy='dynamic', cascade="all")
    message_repliesto = db.relationship('MessageReply', backref='to_user', primaryjoin='MessageReply.to_uid==User.id', lazy='dynamic', cascade="all")
    avatar_row = db.Column(db.String(64))
    avatar_s = db.Column(db.String(64))
    avatar_m = db.Column(db.String(64))
    avatar_l = db.Column(db.String(64))
    albums = db.relationship('Album', backref='author', lazy='dynamic', cascade='all')
    draftss = db.relationship('Draft', backref='author', lazy='dynamic', cascade='all')

    #用户的关注
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower',lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    #用户的粉丝
    followers = db.relationship('Follow',
                               foreign_keys=[Follow.followed_id],
                               backref=db.backref('followed',lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')

    
    def __init__(self,**kwargs):
        super(User, self).__init__(**kwargs)
        self.generate_avatar()
        self.follow(self)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
                
    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions
    
    def is_administrator(self):
        return self.can(Permission.ADMINSTER)



    @property
    def password():
        raise AttributeError('password is not a readable attribute')
        
    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self,password):
        return check_password_hash(self.password_hash, password)
        
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'confirm':self.id})
        
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True
    
    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    @staticmethod
    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True
        
    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True
    
    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)
    
    def generate_avatar(self):
        avatar = Identicon()
        filenames = avatar.generate(text=self.username)
        self.avatar_s = filenames[0]
        self.avatar_m = filenames[1]
        self.avatar_l = filenames[2]
        db.session.commit()
        


            
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        
    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)
            db.session.commit()

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()

    def is_following(self, user):
        if user.id is None:
            return False
        return self.followed.filter_by(
            followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        if user.id is None:
            return False
        return self.followers.filter_by(
            follower_id=user.id).first() is not None
            
    @property
    def followed_posts(self):
        return Post.query.join(Follow,Follow.followed_id == Post.author_id)\
            .filter(Follow.follower_id == self.id)
    
    def __repr__(self):
        return '<User %r>' %self.name

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
    
    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser
 
@login_manager.user_loader
def loader_user(user_id):
    return User.query.get(int(user_id))
        
class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINSTER = 0x80
    
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all')
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    title = db.Column(db.String(64))
    
    
    def post_delete(self, id):
        p = Post.query.filter_by(id=id).first()
        if p:
            db.session.delete(p)
# 草稿箱数据表
class Draft(db.Model):
    __tablename__ = 'drafts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
   

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text) 
    timestamp = db.Column(db.DateTime, index=True,  default=datetime.utcnow)
    disabled = db.Column(db.Boolean) 
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    replies = db.relationship('Reply', backref='comment', lazy='dynamic', cascade='all')
    
    def comment_delete(self):
        db.session.delete(self)
        db.session.commit()


class Reply(db.Model):
    __tablename__ = 'relpies'
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    replyto_id = db.Column(db.Integer)
    replyto_uid = db.Column(db.Integer, db.ForeignKey('users.id'))
    reply_type = db.Column(db.String(64))

    def reply_delete(self):
        db.session.delete(self)
        db.session.commit()
   

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(64), unique=True)
    categories = db.relationship('Category', backref='tag', lazy='dynamic')
    
    def __repr__(self):
        return '<Tag %r>' % self.tag_name

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True, nullable=False)
    posts = db.relationship('Post', backref='category', lazy='dynamic')
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
    drafts = db.relationship('Draft', backref='category', lazy='dynamic')

    def __repr__(self):
        return '<Category %r>' % self.name


    #插入分类和分类的标签
    @staticmethod
    def insert_tags_categories():
        for t, category_1 in tag_category.items():
                tag = Tag.query.filter_by(tag_name=t).first()
                if tag is None:
                    tag = Tag(tag_name=t)
                db.session.add(tag)
                for c in category_1:
                    category = Category.query.filter_by(name=c).first()
                    if category is None:
                        category = Category(name=c,tag_id=tag.id)
                    db.session.add(category)
        db.session.commit()

#分类和分类标签
tag_category = {'生活':['随笔', '足迹', '电影'],
                '技术分享':['Flask', 'Python', 'Django', '前端'],
                }


#留言表
class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id')) 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    replies = db.relationship(' MessageReply', backref='message', lazy='dynamic', cascade='all')
 

class MessageReply(db.Model):
    __tablename__ = "message_replies"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'))
    to_uid = db.Column(db.Integer, db.ForeignKey('users.id'))
    reply_type = db.Column(db.String(64))

class Photo(db.Model):
    __tablename__ = "photos"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    album_id = db.Column(db.Integer, db.ForeignKey('albums.id'))
    filename_s = db.Column(db.String(64))
    filename_m = db.Column(db.String(64))
    cover = db.Column(db.Boolean, default=False)


    @property
    def url(self):
        return photosSet.url(self.filename)
    
    @property
    def url_s(self):
        return photosSet.url(self.filename_s)

    @property
    def url_m(self):
        return photosSet.url(self.filename_m)
    


    def __repr__(self):
        return '<Photo %r>' % self.filename

@db.event.listens_for(Photo, 'after_delete', named=True) #监听图片删除时间，删除对应的文件
def delete_photo(**kwargs):
    target = kwargs['target']
    for filename in [target.filename, target.filename_s, target.filename_m]:
        if filename is not None:
            path = photosSet.path(filename)
            if os.path.exists(path):
                os.remove(path)


class Album(db.Model):
    __tablename__ = "albums"
    id = db.Column(db.Integer, primary_key=True)
    albumname = db.Column(db.String(64))
    decription = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    photos = db.relationship('Photo', backref='album', lazy='dynamic', cascade='all')

    def __repr__(self):
        return '<Album %r>' % self.albumname

"""
@db.event.listen_for(Album, 'after_delete', name=True)
"""