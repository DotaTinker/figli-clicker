from flask_restful import reqparse, abort, Resource
from data.databaseee import User, Collection, NFT
from data import db_session
from flask import jsonify, request
import json
import random
import os
from PIL import Image
from werkzeug.utils import secure_filename

COLLECTION_a = 100
NFT_a = 100
COLL_AND_NFTS_FOLDER = 'collections_and_nfts'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}  # Разрешенные расширения файлов


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
        os.mkdir(folder_name)  # Создаем папку для новой коллекции

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

            collection_image_obj = collection_image_obj.resize((COLLECTION_a, COLLECTION_a))
            collection_image_obj.save(collection_image_path)

            # Создание новой коллекции с именем файла
            collection = Collection(name=collection_name, image_path=collection_image_path_bd)

            # Добавление NFT
            nft_names = request.form.getlist('nft_name[]')
            nft_rarities = request.form.getlist('nft_rarity[]')
            nft_images = request.files.getlist('nft_image[]')

            default_nft_id = db_sess.query(NFT).filter(NFT.collection_id == int(new_collection_id)).count() + 1

            for nft_name, nft_rarity, nft_image in zip(nft_names, nft_rarities, nft_images):
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

                    nft_image_obj = nft_image_obj.resize((NFT_a, NFT_a))
                    nft_image_obj.save(nft_image_path)

                    # Создание NFT с именем файла
                    nft = NFT(name=nft_name, rarity=nft_rarity, image_path=nft_file_name)
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
