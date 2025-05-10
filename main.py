from flask import Flask, render_template, redirect, request, send_from_directory, jsonify
from data import db_session
from data.databaseee import User, Collection, NFT
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.databaseee_forms import SignUpForm, SignInForm
import functools
import os
import json
from flask_restful import Api
from resources import resources
import requests

app = Flask(__name__)
api = Api(app)

api.add_resource(resources.UserSignInResurse, '/api/v2/signin')
api.add_resource(resources.ClickerResource, '/api/clicker/<int:collection_id>/click/<int:user_id>')
api.add_resource(resources.MiningResourse, '/api/mining/<int:user_id>')
api.add_resource(resources.CollectionListResource, '/api/collections')
api.add_resource(resources.UserListResource, '/api/v2/users')

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

COLLECTION_a = 100
NFT_a = 100
COLL_AND_NFTS_FOLDER = 'collections_and_nfts'  # Папка для сохранения изображений нфт
# /uploads
#   /имя коллекции
#     имя коллекции.png
#     /nfts
#       имя нфт.png
#       ...
#   ...
os.makedirs(COLL_AND_NFTS_FOLDER, exist_ok=True)
USERS_JSONS = 'users_jsons'  # Папка для сохранения json-файлов о пользователях
# наименование json'а - почта пользователя (Amogus@amogus.json)
# json хранит информацию о том, какие nft (тоесть их id) есть у пользователя
# {"имя коллекции":
#     {"имя nft": колличество,
#     "имя nft": колличество,
#     ...},
# ...}
os.makedirs(USERS_JSONS, exist_ok=True)
USERS_PHOTOS = 'users_photos'  # Папка для сохранения изображений профиля пользователей, имя - почта
os.makedirs(USERS_PHOTOS, exist_ok=True)
login_manager = LoginManager()
login_manager.init_app(app)


def admin_required(f):  # декоратор недопускающий людей без прав администратора
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_function


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(COLL_AND_NFTS_FOLDER, filename)


@app.route('/signin', methods=['GET', 'POST'])
def login():
    form = SignInForm()
    if form.validate_on_submit():
        data = {
            'email': request.form.get('email'),
            'password': request.form.get('password'),
        }
        response = requests.post('http://localhost:8080//api/v2/signin', json=data)
        if response.status_code == 200:
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.email == form.email.data).first()
            login_user(user, remember=form.remember_me.data)
            return redirect('/')

    return render_template('signin.html', title='Авторизация', form=form)


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        if form.password1.data != form.password2.data:
            return render_template('signup.html', form=form, message="Пароли не совпадают")

        for el in r"""\|/:*?"<>""":
            if el in form.email.data:
                return render_template('signup.html', form=form, message=r"""Нельзя в emeil юзать \|/:*?"<>""")

        db_sess = db_session.create_session()

        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('signup.html', form=form, message="Такой пользователь уже есть")
        if db_sess.query(User).filter(User.user_name == form.user_name.data).first():
            return render_template('signup.html', form=form, message="Такой пользователь уже есть")

        data = {
            'name': request.form.get('name'),
            'user_name': request.form.get('user_name'),
            'email': request.form.get('email'),
            'password': request.form.get('password1'),
        }

        response = requests.post('http://localhost:8080/api/v2/users', json=data)
        if response.status_code == 201:
            return redirect('/signin')

        message = response.json().get('message', 'Ошибка при регистрации')
        return render_template('signup.html', form=SignUpForm(), message=message)

    return render_template('signup.html', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/index')
@app.route('/')
def index():
    db_sess = db_session.create_session()
    collections = db_sess.query(Collection).all()
    return render_template('home.html', collections=collections)


@app.route('/clicker/<int:collection_id>', methods=['GET'])
@login_required
def clicker(collection_id):
    db_sess = db_session.create_session()
    collection = db_sess.query(Collection).filter(Collection.id == collection_id).first()

    if not collection:
        return redirect("/")

    return render_template('clicker.html', collection=collection)


@app.route('/mining', methods=['GET'])
@login_required
def mining():
    return render_template('mining.html', coins=current_user.figli_coins)


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


@app.route('/add-collections', methods=['GET', 'POST'])
@login_required
@admin_required
def add_collections():
    return render_template('add-collections.html')


@app.route("/profile/<string:user_name>", methods=["GET", "POST"])
@login_required
def profile(user_name):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.user_name == user_name).first()
    if user:
        with open(f"./users_jsons/{user.email}.json") as user_json:
            return render_template("profile.html",
                                   User=user, json=json.load(user_json))


if __name__ == '__main__':
    db_session.global_init("db/databasee.db")
    app.run(port=8080, host='127.0.0.1')
