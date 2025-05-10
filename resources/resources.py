import pprint

from flask_restful import reqparse, abort, Resource
from data.databaseee import User, Collection, NFT
from data import db_session
from flask import jsonify, request
import json
import random
import os
from PIL import Image
from werkzeug.utils import secure_filename
import Brawlers

COLLECTION_a = 100
NFT_a = 100
COLL_AND_NFTS_FOLDER = 'collections_and_nfts'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}  # Разрешенные расширения файлов

user_parser = reqparse.RequestParser()
user_parser.add_argument('name', required=True)
user_parser.add_argument('user_name', required=True)
user_parser.add_argument('email', required=True)
user_parser.add_argument('password', required=True)


def norm_list(ne_norm_list):
    while True:
        fl2 = True
        if 'on' in ne_norm_list:
            for i in range(len(ne_norm_list)):
                if ne_norm_list[i] == 'on':
                    ne_norm_list[i] = '_on'
                    ne_norm_list.pop(i - 1)
                    fl2 = False
                    break
        if fl2:
            return ne_norm_list # ну он не ненормальный список возрващвет, а уже нормальный, ну кароче переменная такая

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


def abort_if_collection_not_found(collection_id):
    session = db_session.create_session()
    collection = session.query(Collection).get(collection_id)
    if not collection:
        abort(404, message=f"Collection {collection_id} not found")


def abort_if_nft_not_found(nft_id):
    session = db_session.create_session()
    nft = session.query(NFT).get(nft_id)
    if not nft:
        abort(404, message=f"NFT {nft_id} not found")


class UserResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict(only=('id', 'name', 'user_name', 'email'))})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})

class UserListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict(only=('id', 'name', 'user_name', 'email')) for item in users]})

    def post(self):
        args = user_parser.parse_args()
        session = db_session.create_session()
        user = User(
            name=args['name'],
            user_name=args['user_name'],
            email=args['email']
        )
        user.set_password(args['password'])
        session.add(user)
        session.commit()
        with open(f"./users_jsons/{args['email']}.json", "w") as new_user_json:
            json.dump({}, new_user_json)
        return {'id': user.id}, 201


class UserSignInResurse(Resource):
    def post(self):
        data = request.get_json()

        if not data or 'email' not in data or 'password' not in data:
            return {'message': 'Email и пароль обязательны'}, 400

        email = data['email']
        password = data['password']

        session = db_session.create_session()
        user = session.query(User).filter(User.email == email).first()

        if user is None or not user.check_password(password):
            return {'message': 'Неверный email или пароль'}, 401
        return {'message': 'Успешный вход', 'user_id': user.id}, 200


class CollectionListResource(Resource):
    def post(self):
        collection_name = request.form['collection_name']  # Имя коллекции
        collection_image = request.files['collection_image']  # Файл изображения коллекции

        if not allowed_file(collection_image.filename):
            return {'error': 'Разрешены только файлы формата PNG или JPG'}, 400

        extension = os.path.splitext(secure_filename(collection_image.filename))[-1]
        db_sess = db_session.create_session()
        new_collection_id = str(db_sess.query(Collection).count() + 1)  # Получаем новый ID для коллекции

        folder_name = os.path.join(COLL_AND_NFTS_FOLDER, new_collection_id)
        '''os.mkdir(folder_name)'''  # Создаем папку для новой коллекции

        file_name = f"{new_collection_id}{extension}"
        collection_image_path = os.path.join(folder_name, file_name)
        collection_image_path_bd = f"{new_collection_id}/{file_name}"

        try:
            collection_image.save(collection_image_path)

            # Изменение размеров картинки до соотношения сторон 1:1
            collection_image_obj = Image.open(collection_image_path)
            width, height = collection_image_obj.size

            if width != height:
                min_side = min(width, height)
                min_side -= min_side % 2
                collection_image_obj = collection_image_obj.crop((0, 0, min_side, min_side))

            collection_image_obj.save(collection_image_path)

            # Создание новой коллекции с именем файла
            collection = Collection(name=collection_name, image_path=collection_image_path_bd)

            # Добавление NFT
            nft_names = request.form.getlist('nft_name[]')
            nft_rarities = request.form.getlist('nft_rarity[]')
            nft_images = request.files.getlist('nft_image[]')

            rs = norm_list(request.form.getlist("rare"))
            srs = norm_list(request.form.getlist("super_rare"))
            es = norm_list(request.form.getlist("epic"))
            ms = norm_list(request.form.getlist("mythic"))
            ls = norm_list(request.form.getlist("legendary"))

            hs = norm_list(request.form.getlist("healer"))
            ss = norm_list(request.form.getlist("sniper"))
            ds = norm_list(request.form.getlist("damage_dealer"))
            ts = norm_list(request.form.getlist("tank"))
            pprint.pprint([rs, srs, es, ms, ls, hs, ss, ds, ts])
            default_nft_id = db_sess.query(NFT).filter(NFT.collection_id == int(new_collection_id)).count() + 1
            for nft_name, nft_rarity, nft_image, r, sr, e, m, l, h, s, d, t in zip(nft_names, nft_rarities, nft_images, rs, srs, es, ms, ls, hs, ss, ds, ts):
                if not allowed_file(nft_image.filename):
                    raise ValueError(f'Файл {nft_name} имеет недопустимый формат. Разрешены только PNG или JPG.')

                nft_extension = os.path.splitext(secure_filename(nft_image.filename))[-1]
                nft_folder_path = os.path.join(folder_name, 'nfts')
                os.makedirs(nft_folder_path, exist_ok=True)  # Создаем папку для NFT

                new_nft_id = str(default_nft_id)
                nft_file_name = f"{new_nft_id}{nft_extension}"
                nft_image_path = os.path.join(nft_folder_path, nft_file_name)

                try:
                    nft_image.save(nft_image_path)

                    nft_image_obj = Image.open(nft_image_path)
                    width, height = nft_image_obj.size

                    if width != height:
                        min_side = min(width, height)
                        min_side -= min_side % 2
                        nft_image_obj = nft_image_obj.crop((0, 0, min_side, min_side))

                    nft_image_obj.save(nft_image_path)

                    nft_brawler_rarities = []
                    for i, el in enumerate([r, sr, e, m , l]):
                        if el:
                            nft_brawler_rarities.append(str(i))

                    nft_brawler_classes = []
                    for i, el in enumerate([h, s, d, t]):
                        if el:
                            nft_brawler_classes.append(str(i))
                    # Создание NFT с именем файла
                    nft = NFT(name=nft_name, rarity=nft_rarity, image_path=nft_file_name, classes_as_brawler=" ".join(nft_brawler_classes), rarities_as_brawler=" ".join(nft_brawler_rarities))
                    collection.nfts.append(nft)
                    default_nft_id += 1

                except Exception as e:
                    return {'error': f'Ошибка при обработке NFT {nft_name}: {str(e)}'}, 500

            db_sess.add(collection)
            db_sess.commit()

            return {'message': 'Коллекция успешно добавлена'}, 201

        except Exception as e:
            # Удаляем созданную папку и все её содержимое в случае ошибки
            if os.path.exists(folder_name):
                import shutil
                shutil.rmtree(folder_name)

            return {'error': 'Произошла ошибка при добавлении коллекции: {}'.format(str(e))}, 500


class ClickerResource(Resource):

    def post(self, collection_id, user_id):
        db_sess = db_session.create_session()

        # Получаем коллекцию
        collection = db_sess.query(Collection).filter(Collection.id == collection_id).first()
        if not collection:
            return {'message': 'Collection not found'}, 404

        # Получаем пользователя по user_id
        user = db_sess.query(User).filter(User.id == user_id).first()
        if not user:
            return {'message': 'User not found'}, 404

        # Увеличиваем счетчик нажатий пользователя
        user.click_count = (user.click_count or 0) + 1
        db_sess.merge(user)
        db_sess.commit()

        rarity_percents = {"rare": user.rare, "super_rare": user.super_rare, "epic": user.epic, "mythic": user.mythic, "legendary": user.legendary, "": user.none}
        rarity_strike = {"rare": user.rare_s, "super_rare": user.super_rare_s, "epic": user.epic_s, "mythic": user.mythic_s, "legendary": user.legendary_s, "": user.none_s}
        _rarity = random.choices(list(rarity_percents.keys()), weights=list(rarity_percents.values()))[0]
        rarity_strike, rarity_percents = Brawlers.chance_rarity_changer(_rarity, rarity_strike, rarity_percents)

        for k, v in rarity_percents.items():
            if k == "rare":
                user.rare = v
            elif k == "super_rare":
                user.super_rare = v
            elif k == "epic":
                user.epic = v
            elif k == "mythic":
                user.mythic = v
            elif k == "legendary":
                user.legendary = v
            else:
                user.none = v
            db_sess.commit()

        for k, v in rarity_strike.items():
            if k == "rare":
                user.rare_s = v
            elif k == "super_rare":
                user.super_rare_s = v
            elif k == "epic":
                user.epic_s = v
            elif k == "mythic":
                user.mythic_s = v
            elif k == "legendary":
                user.legendary_s = v
            else:
                user.none_s = v
            db_sess.commit()

        if _rarity:
            classes_percent = {"healer": user.healer, "damage_dealer": user.damage_dealer, "sniper": user.sniper, "tank": user.tank}
            classes_strike = {"healer": user.healer_s, "damage_dealer": user.damage_dealer_s, "sniper": user.sniper_s, "tank": user.tank_s}

        nft_received = None

        # Логика выпадения NFT
        if random.random() < 0.10:  # 10% шанс на выпадение NFT
            rarity_roll = random.random()
            if rarity_roll < 0.005:
                rarity = 'godlike'
            elif rarity_roll < 0.01:
                rarity = 'legendary'
            elif rarity_roll < 0.06:
                rarity = 'epic'
            elif rarity_roll < 0.16:
                rarity = 'rare'
            elif rarity_roll < 0.46:
                rarity = 'uncommon'
            else:
                rarity = 'common'

            nfts_of_rarity = db_sess.query(NFT).filter(
                NFT.collection_id == collection.id,
                NFT.rarity == rarity
            ).all()

            if nfts_of_rarity:
                nft_received = random.choice(nfts_of_rarity)

                user_inventory_path = f"./users_jsons/{user.email}.json"

                if os.path.exists(user_inventory_path):
                    with open(user_inventory_path, "r") as user_json:
                        inventory_data = json.load(user_json)
                else:
                    inventory_data = {}

                collection_name = collection.name

                if collection_name not in inventory_data:
                    inventory_data[collection_name] = {}

                nft_name = nft_received.name

                if nft_name in inventory_data[collection_name]:
                    inventory_data[collection_name][nft_name] += 1
                else:
                    inventory_data[collection_name][nft_name] = 1

                with open(user_inventory_path, "w") as user_json:
                    json.dump(inventory_data, user_json)

        response_data = {
            'click_count': user.click_count,
            'nft_received': {
                'id': nft_received.id,
                'name': nft_received.name,
                'rarity': nft_received.rarity,
            } if nft_received else None
        }

        return response_data, 200


class MiningResourse(Resource):
    def post(self, user_id):
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == user_id).first()
        if not user:
            return {'message': 'User not found'}, 404

        user.figli_coins += 1

        db_sess.merge(user)
        db_sess.commit()

        return jsonify({'coins': user.figli_coins})
