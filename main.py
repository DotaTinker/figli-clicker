from flask import Flask, render_template, redirect, flash, request
from data import db_session
from data.users import User
from data.nftdb import Collection, NFT
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.user_forms import SignUpForm, SignInForm
import functools
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
UPLOAD_FOLDER = 'uploads'  # Папка для сохранения загруженных изображений
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
login_manager = LoginManager()
login_manager.init_app(app)


def admin_required(f):  # декоратор недопускающий людей без прав администратора
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("У вас нет прав для доступа к этой странице.", "danger")
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_function


@app.route('/signin', methods=['GET', 'POST'])
def login():
    form = SignInForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('signin.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('signin.html', title='Авторизация', form=form)


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        if form.password1.data != form.password2.data:
            return render_template('signup.html', form=form, message="Пароли не совпадают")

        db_sess = db_session.create_session()

        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('signup.html', form=form, message="Такой пользователь уже есть")

        user = User(name=form.name.data,
                    user_name=form.name.data,
                    email=form.email.data)
        user.set_password(form.password1.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/signin')
    return render_template('signup.html', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/index')
@app.route('/')
@login_required
def index():
    return render_template("base.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/nftmanage")
@login_required
@admin_required
def nftmanage():
    return render_template("nftmanage.html")


@login_required
@admin_required
@app.route('/add-collections', methods=['GET', 'POST'])
def add_collections():
    return render_template('add-collections.html')


if __name__ == '__main__':
    db_session.global_init("db/users.db")
    db_session.global_init("db/nft_collections.db")
    app.run(port=8080, host='127.0.0.1')
