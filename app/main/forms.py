from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from ..models import Role, User, Category, Comment, Reply
from flask_pagedown.fields import PageDownField

class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0,64)])
    location = StringField('Location', validators=[Length(0,64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')
    
class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

class CommentForm(FlaskForm):
    body = StringField('', validators=[Required()])
    submit = SubmitField('Submit')
    
class PostForm(FlaskForm):
    title = StringField("标题", validators=[Required()])
    body = TextAreaField("")
    category = SelectField("分类", validators=[Required()], coerce=int)
    submit = SubmitField('Submit')
    
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name) for category in Category.query.all()]

class ReplyForm(FlaskForm):
    body = TextAreaField("", validators=[Required()])
    submit = SubmitField('提交')


class MessageForm(FlaskForm):
    body = TextAreaField("留言", validators=[Required()])
    submit = SubmitField('提交')


class AlbumForm(FlaskForm):
    albumname = StringField("相册名", validators=[Required()])
    decription = TextAreaField("相册描述", validators=[Required()])
    submit = SubmitField('提交')