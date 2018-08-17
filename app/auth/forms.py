from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

class LoginForm(FlaskForm):
    email = StringField('邮箱地址', validators=[Required(), Length(1,64),
                                             Email()])
    password = PasswordField('密码', validators=[Required()])
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
    old_password = PasswordField('Old password', validators=[Required()])
    password = PasswordField('New password', validators=[
        Required(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm new password', validators=[Required()])
    submit = SubmitField('Update Password')
    
class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    submit = SubmitField('Reset Password')


class PasswordResetForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    password = PasswordField('New Password', validators=[
        Required(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Reset Password')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')
