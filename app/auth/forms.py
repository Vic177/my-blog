from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired
from ..models import User

class LoginForm(FlaskForm):
    email = StringField('', validators=[Required(), Length(1,64),
                                             Email()])
    password = PasswordField('', validators=[Required()])
    remember_me = BooleanField('记住密码')
    submit = SubmitField('登陆')

class RegistrationForm(FlaskForm):
    email = StringField('邮箱地址', validators=[Required(), Length(1,64),
                                             Email()])
    username = StringField('用户名', validators=[Required(),
        Length(1,64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 
                             'Username must have only letters, numbers, dots or underscores')])
    password = PasswordField('密码', validators=[Required(),
        EqualTo('password2', message='Password must match,')])
    password2 = PasswordField('确认密码', validators=[Required()])
    submit = SubmitField('注册')
    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已注册！')
            
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已存在！')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[Required()])
    password = PasswordField('新密码', validators=[
        Required(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('确认密码', validators=[Required()])
    submit = SubmitField('修改密码')
    
class PasswordResetRequestForm(FlaskForm):
    email = StringField('邮箱地址', validators=[Required(), Length(1, 64),
                                             Email()])
    submit = SubmitField('确认')


class PasswordResetForm(FlaskForm):
    email = StringField('邮箱地址', validators=[Required(), Length(1, 64),
                                             Email()])
    password = PasswordField('新密码', validators=[
        Required(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('确认密码', validators=[Required()])
    submit = SubmitField('重置密码')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')
            
class ChangeEmailForm(FlaskForm):
    email = StringField('新邮箱', validators=[Required(), Length(1, 64),
                                                 Email()])
    password = PasswordField('密码', validators=[Required()])
    submit = SubmitField('更改邮箱地址')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

class UploadAvatarForm(FlaskForm):
    image = FileField('图片大小请不要超过3M!', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'The file format should be .jpg .png')])
    submit = SubmitField('确认上传')

class CropAvatarForm(FlaskForm):
    x = HiddenField()
    y = HiddenField()
    w = HiddenField()
    h = HiddenField()
    submit = SubmitField('剪切并上传')
