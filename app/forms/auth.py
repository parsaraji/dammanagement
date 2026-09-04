from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('نام کاربری', validators=[DataRequired(message='لطفاً نام کاربری را وارد کنید.')])
    password = PasswordField('رمز عبور', validators=[DataRequired(message='لطفاً رمز عبور را وارد کنید.')])
    submit = SubmitField('ورود به سیستم')
