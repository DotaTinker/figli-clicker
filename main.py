from flask import Flask, render_template, redirect, request, send_from_directory, jsonify
from data import db_session
from data.databaseee import User, Collection, NFT
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.databaseee_forms import SignUpForm, SignInForm
import functools
import os
from werkzeug.utils import secure_filename
import json
from PIL import Image
import random
from flask_restful import reqparse, abort, Api, Resource
from resources import resources
import requests

app = Flask(__name__)
api = Api(app)

api.add_resource(resources.UserListResource, '/api/v2/users')
api.add_resource(resources.UserSignInResurse, '/api/v2/signin')
api.add_resource(resources.ClickerResource, '/api/clicker/<int:collection_id>/click/<int:user_id>')
api.add_resource(resources.MiningResourse, '/api/mining/<int:user_id>')

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
    if request.method == 'POST':
        collection_name = request.form['collection_name']  # имя
        collection_image = request.files['collection_image']  # файл

        extension = ''
        for el in secure_filename(collection_image.filename)[::-1]:
            extension += el
            if el == '.':
                extension = extension[::-1]
                break
        # здесь получил расширение файла
        db_sess = db_session.create_session()
        new_collection_id = str(db_sess.query(Collection).count() + 1)  # Получаем новый ID для коллекции

        try:
            folder_name = os.path.join(COLL_AND_NFTS_FOLDER, new_collection_id)
            os.mkdir(folder_name)  # Создаем папку для новой коллекции

            file_name = f"{new_collection_id}{extension}"
            collection_image_path = os.path.join(folder_name, file_name)
            collection_image_path_bd = f"{new_collection_id}/{file_name}"
            collection_image.save(collection_image_path)

            # Изменение размеров картинки до соотношения сторон 1:1
            collection_image = Image.open(collection_image_path)
            width, height = collection_image.size

            if width != height:
                min_side = min(width, height)
                min_side -= min_side % 2
                collection_image = collection_image.crop((0, 0, min_side, min_side))

            collection_image = collection_image.resize((COLLECTION_a, COLLECTION_a))
            collection_image.save(collection_image_path)

            # Создание новой коллекции с именем файла
            collection = Collection(name=collection_name, image_path=collection_image_path_bd)

            # Добавление NFT
            nft_names = request.form.getlist('nft_name[]')
            nft_rarities = request.form.getlist('nft_rarity[]')
            nft_images = request.files.getlist('nft_image[]')

            default_nft_id = db_sess.query(NFT).filter(NFT.collection_id == int(new_collection_id)).count() + 1
            for nft_name, nft_rarity, nft_image in zip(nft_names, nft_rarities, nft_images):
                nft_extension = ''
                for el in secure_filename(nft_image.filename)[::-1]:
                    nft_extension += el
                    if el == '.':
                        nft_extension = nft_extension[::-1]
                        break
                nft_folder_path = os.path.join(folder_name, 'nfts')
                os.makedirs(nft_folder_path, exist_ok=True)  # Создаем папку для NFT

                new_nft_id = str(default_nft_id)
                nft_file_name = f"{new_nft_id}{nft_extension}"
                nft_image_path = os.path.join(nft_folder_path, nft_file_name)
                nft_image.save(nft_image_path)

                nft_image = Image.open(nft_image_path)
                width, height = nft_image.size

                if width != height:
                    min_side = min(width, height)
                    min_side -= min_side % 2
                    nft_image = nft_image.crop((0, 0, min_side, min_side))

                nft_image = nft_image.resize((NFT_a, NFT_a))
                nft_image.save(nft_image_path)

                # Создание NFT с именем файла
                nft = NFT(name=nft_name, rarity=nft_rarity, image_path=nft_image_path)
                collection.nfts.append(nft)
                default_nft_id += 1

            db_sess.add(collection)
            db_sess.commit()

            return redirect('/')

        except Exception as e:
            print(str(e))
            return redirect('/add-collections')

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
