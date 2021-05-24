from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import PasswordField, BooleanField, SubmitField, StringField


class RegisterForm(FlaskForm):
    """Создает форму регистрации"""
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    repeat_password = PasswordField('Пароль еще раз', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Зарегистрироваться')
