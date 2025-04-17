from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired


class SignUpForm(FlaskForm):  # SignUp - зарегаться, твоего акка ещё нет в бд
    email = EmailField('Email:', validators=[DataRequired()])
    password1 = PasswordField('Придумайте пароль: ', validators=[DataRequired()])
    password2 = PasswordField('Введите пароль повторно: ', validators=[DataRequired()])
    name = StringField('Придумайте ваше имя: ', validators=[DataRequired()])
    user_name = StringField('Имя пользователя: ', validators=[DataRequired()])
    submit = SubmitField('Зарегестрироваться')



class SignInForm(FlaskForm):  # SignIn - войти, когда ты уже есть в базе данных
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
