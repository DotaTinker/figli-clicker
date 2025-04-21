from flask import Flask, render_template, redirect, flash, request, send_from_directory, jsonify
from data import db_session
from data.databaseee import User, Collection, NFT
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.databaseee_forms import SignUpForm, SignInForm
import functools
import os
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
UPLOAD_FOLDER = 'uploads'  # Папка для сохранения изображений нфт
# /uploads
#   /имя коллекции
#     имя коллекции.png
#     /nfts
#       имя нфт.png
#       ...
#   ...
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
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
            flash("У вас нет прав для доступа к этой странице.", "danger")
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_function


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


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

        for el in r"""\|/:*?"<>""":
            if el in form.email.data:
                return render_template('signup.html', form=form, message=r"""Нельзя в emeil юзать \|/:*?"<>""")

        db_sess = db_session.create_session()

        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('signup.html', form=form, message="Такой пользователь уже есть")

        user = User(name=form.name.data,
                    user_name=form.name.data,
                    email=form.email.data)
        user.set_password(form.password1.data)
        db_sess.add(user)
        db_sess.commit()

        with open(f"./users_jsons/{form.email.data}.json", "w") as new_user_json:
            json.dump({}, new_user_json)

        return redirect('/signin')
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


@app.route('/clicker/<int:collection_id>')
@login_required
def clicker(collection_id):
    # Здесь будет логика для обработки нажатия на коллекцию
    return f'Вы нажали на коллекцию с ID: {collection_id}'


@login_required
@app.route('/mining', methods=['GET', 'POST'])
def mining():
    db_sess = db_session.create_session()

    if request.method == "POST":

        current_user.figli_coins += 1

        db_sess.merge(current_user)
        db_sess.commit()

        return jsonify({'coins': current_user.figli_coins})

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
        collection_name = request.form['collection_name']

        # Сохранение изображения коллекции
        collection_image = request.files['collection_image']
        collection_image_filename = secure_filename(collection_image.filename)
        collection_image_path = os.path.join(UPLOAD_FOLDER, collection_image_filename)

        try:
            collection_image.save(collection_image_path)

            # Создание новой коллекции с именем файла
            db_sess = db_session.create_session()
            collection = Collection(name=collection_name, image_path=collection_image_filename)

            # Добавление NFT
            nft_names = request.form.getlist('nft_name[]')
            nft_rarities = request.form.getlist('nft_rarity[]')
            nft_images = request.files.getlist('nft_image[]')

            for nft_name, nft_rarity, nft_image in zip(nft_names, nft_rarities, nft_images):
                nft_image_filename = secure_filename(nft_image.filename)
                nft_image_path = os.path.join(UPLOAD_FOLDER, nft_image_filename)
                nft_image.save(nft_image_path)

                # Создание NFT с именем файла
                nft = NFT(name=nft_name, rarity=nft_rarity, image_path=nft_image_filename)
                collection.nfts.append(nft)

            db_sess.add(collection)
            db_sess.commit()

            flash("Коллекция успешно добавлена!", "success")
            return redirect('/')

        except Exception as e:
            flash(f"Произошла ошибка: {str(e)}", "danger")
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
