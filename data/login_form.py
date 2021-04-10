from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import PasswordField, BooleanField, SubmitField, StringField


class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
