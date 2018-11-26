from flask import render_template, session, redirect, url_for, flash, request, \
    current_app, send_from_directory, flash, jsonify
from ..models import User, Role, Post, Permission, Comment, Category, Reply, \
                     Message
from ..models import Album, Photo
from .forms import EditProfileForm, PostForm, CommentForm, EditProfileAdminForm, ReplyForm, \
                   MessageForm, AlbumForm
from flask_login import login_required, current_user
from ..decorators import admin_required, permission_required
from flask_dropzone import random_filename
from ..utils import resize_image

from .. import db, photosSet

from .. import moment

from . import main 
import os

@main.route('/', methods=['GET','POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(title=form.title.data,
                    body=form.body.data,
                    category=Category.query.get(form.category.data),
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    admin = User.query.filter(Role.name=="Administrator").first()
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page,
        per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('index.html', posts=posts, admin=admin, pagination=pagination, form=form)
    
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    posts = Post.query.filter_by(author=user).order_by(Post.timestamp.desc()).all()
    if user is None:
        abort(404)
    return render_template('user.html', user=user, posts=posts)
    
@main.route('/edit-profile', methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash('Your profile has been updated.')
        return render_template('edit_profile.html', form=form)
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)
    
@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if request.method == 'POST':
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        timestamp = moment.create(comment.timestamp).format('YY-MM-DD HH:mm') #在视图函数中渲染时间戳
        return render_template('_com.html', comment=comment, timestamp=timestamp) 
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) / \
            current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)
    
@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    return render_template('edit_post.html', form=form)
    
@main.route('/post/<int:id>/delete')
@login_required
def post_delete(id):
    post = Post.query.get_or_404(id)
    if current_user == post.author or current_user.can(Permission.ADMINISTER):
        post.post_delete(id)
        flash('文章删除成功！')
    return redirect(url_for('.index'))

@main.route('/comment/<int:id>/delete')
@login_required
def comment_delete(id):
    comment = Comment.query.get_or_404(id)
    post_id = comment.post.id
    if current_user == comment.author or current_user.can(Permission.ADMINISTER):
        comment.comment_delete()
        flash('评论删除成功！')
    return redirect(url_for('.post', id=post_id))

@main.route('/reply/<int:id>/delete')
@login_required
def reply_delete(id):
    reply = Reply.query.get_or_404(id)
    post_id = reply.post.id
    if current_user == reply.author or current_user.can(Permission.ADMINISTER):
        reply.reply_delete()
        flash('回复删除成功！')
    return redirect(url_for('.post', id=post_id))

@main.route('/category/<name>')
def category(name):
    category = Category.query.filter_by(name=name).first()
    posts = Post.query.filter_by(category=category).order_by(Post.timestamp.desc()).all()
    return render_template('category.html', posts=posts, category=category)


@main.route('/reply-comment/<int:id>', methods=['POST'])
@login_required
def reply_comment(id):
    comment = Comment.query.get_or_404(id)
    if request.method == 'POST':
        reply = Reply(body=request.form.get('body'),
                      comment=comment,
                      author=current_user._get_current_object(),
                      replyto_id=comment.id,
                      replyto_user=comment.author,
                      reply_type = 'comment'
                      )
        db.session.add(reply)
        db.session.commit()
        timestamp = moment.create(reply.timestamp).format('YY-MM-DD HH:mm:ss')
        return render_template("_reply.html", reply=reply, timestamp=timestamp)

@main.route('/reply-reply/<int:id>', methods=['GET', 'POST'])
@login_required
def reply_reply(id):
    reply = Reply.query.get_or_404(id)
    if request.method == 'POST':
        reply1 = Reply(body=request.form.get('body'),
                        comment=reply.comment,
                        author=current_user._get_current_object(),
                        replyto_id=reply.id,
                        replyto_user=reply.author,
                        reply_type='reply')
        db.session.add(reply1)
        db.session.commit()
        timestamp = moment.create(reply1.timestamp).format('YY-MM-DD HH:mm:ss')
        return render_template("_reply.html", reply=reply1, timestamp=timestamp)

@main.route('/write_post/', methods=['GET', 'POST'])
def write_post():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(title=form.title.data,
                    body=form.body.data,
                    category=Category.query.get(form.category.data),
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('write_post.html', form=form)

@main.route('/follow/<username>', methods=['GET', 'POST'])
def follow(username):
    if not current_user.is_authenticated:
        return jsonify(message='Login Required'), 403
    if not current_user.confirmed:
        return jsonify(message='Confirmed account required.'), 400
    if not current_user.can(Permission.FOLLOW):
        return jsonify(message='No permission.'), 403

    user = User.query.filter_by(username=username).first_or_404()
    if current_user.is_following(user):
        return jsonify(message='Already followed.'), 400
    current_user.follow(user)
    return jsonify(message=('已关注 ' + user.username))


@main.route('/unfollow/<username>', methods=['GET', 'POST'])
def unfollow(username):
    if not current_user.is_authenticated:
        return jsonify(message='Login Required'), 403
    if not current_user.confirmed:
        return jsonify(message='Confirmed account required.'), 400
    if not current_user.can(Permission.FOLLOW):
        return jsonify(message='No permission.'), 403

    user = User.query.filter_by(username=username).first_or_404()
    if not current_user.is_following(user):
        return jsonify(message='Not follow yet.'), 400
    current_user.unfollow(user)
    return jsonify(message=('已取消关注对  ' + user.username + ' 的关注'))

@main.route('/update-followers-count/<int:user_id>')
def update_followers_count(user_id):
    user = User.query.get_or_404(user_id)
    count = user.followers.count() - 1 #用户关注自己要减去
    return jsonify(count=count)


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


@main.route('/avatars/<path:filename>')
def get_avatar(filename):
    return send_from_directory(current_app.config['AVATARS_SAVE_PATH'], filename)

@main.route('/images/<path:filename>')
def  get_image(filename):
    return send_from_directory(current_app.config['IMAGE_SAVE_PATH'], filename)

@main.route('/upload', methods=['GET', 'POST']) #文章图片上传
@login_required
def upload():
    if request.method == 'POST':
        f = request.files.get('file')
        filename = random_filename(f.filename)
        f.save(os.path.join(current_app.config['IMAGE_SAVE_PATH'], filename))
        url = url_for('main.get_image', filename=filename)
        return jsonify( location = url )



@main.route('/album/<int:user_id>', methods=['GET', 'POST'])
@login_required
def album(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    albums = Album.query.filter_by(author=user).all()
    form = AlbumForm()
    if form.validate_on_submit():
        album = Album(albumname=form.albumname.data,
                      decription=form.decription.data,
                      author=current_user._get_current_object())
        db.session.add(album)
        db.session.commit()
        return redirect(url_for('main.upload_photos', album_id=album.id))
    return render_template('album.html', form=form, albums=albums, user=user)

@main.route('/upload-photos/<int:album_id>', methods=['GET', 'POST'])
@login_required
def upload_photos(album_id):
    album = Album.query.filter_by(id=album_id).first_or_404()
    if request.method == 'POST' and 'file' in request.files:
        f = request.files.get('file')
        filename = random_filename(f.filename)
        folder = album.author.username + '/' + album.albumname
        fname = photosSet.save(f, folder=folder, name=filename)
        filename_s = resize_image(f, fname, 200)
        filename_m = resize_image(f, fname, 800)
        photo = Photo(filename=fname,
                      album=album,
                      filename_s=filename_s,
                      filename_m=filename_m)
        db.session.add(photo)
        db.session.commit()
    return render_template('upload_photos.html', album=album)

@main.route('/album_show/<int:album_id>', methods=['GET', 'POST'])
@login_required
def album_show(album_id):
    album = Album.query.filter_by(id=album_id).first_or_404()
    photos = Photo.query.filter_by(album_id=album_id).all()
    form = AlbumForm()
    if request.method == 'POST':
        album.albumname = form.albumname.data
        album.decription = form.decription.data
        db.session.add(album)
        db.session.commit()
        albumname = album.albumname
        decription = album.decription
        message = "修改成功！"
        return jsonify(albumname=albumname, decription=decription, message=message)
    return render_template('album_show.html', album=album, photos=photos, form=form)

"""
@main.route('/get_photo/<path:filename>')
def get_photo(filename):
    return photosSet.url(filename)
"""

@main.route('/delete/photo/<int:photo_id>', methods=['GET', 'POST'])
@login_required
def delete_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if current_user != photo.album.author:
        abort(404)
    db.session.delete(photo)
    db.session.commit()
    flash('图片已删除！')
    return redirect(url_for('.album_show', album_id = photo.album.id))

@main.route('/delete/album/<int:album_id>', methods=['POST', 'GET'])
@login_required
def delete_album(album_id):
    album = Album.query.get_or_404(album_id)
    if current_user != album.author:
        abort(404)
    db.session.delete(album)
    db.session.commit()
    flash('相册已删除！')
    return redirect(url_for('.album', user_id=album.author.id))
