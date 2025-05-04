from flask_restful import reqparse, abort, Api, Resource
from data.databaseee import User, Collection, NFT
from data import db_session
from flask import jsonify, request
import json
from flask_login import login_required, current_user
import random
import os

parser = reqparse.RequestParser()
parser.add_argument('name', type=str, required=True, help='Name cannot be blank')
parser.add_argument('user_name', type=str, required=True, help='User name cannot be blank')
parser.add_argument('email', type=str, required=True, help='Email cannot be blank')
parser.add_argument('hashed_password', type=str, required=True, help='Password cannot be blank')

user_parser = reqparse.RequestParser()
user_parser.add_argument('name', required=True)
user_parser.add_argument('user_name', required=True)
user_parser.add_argument('email', required=True)
user_parser.add_argument('password', required=True)

collection_parser = reqparse.RequestParser()
collection_parser.add_argument('name', required=True)
collection_parser.add_argument('image_path', required=True)

nft_parser = reqparse.RequestParser()
nft_parser.add_argument('name', required=True)
nft_parser.add_argument('rarity', required=True)
nft_parser.add_argument('image_path', required=True)
nft_parser.add_argument('collection_id', required=True, type=int)


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


class CollectionResource(Resource):
    def get(self, collection_id):
        abort_if_collection_not_found(collection_id)
        session = db_session.create_session()
        collection = session.query(Collection).get(collection_id)
        return jsonify({'collection': collection.to_dict(only=('id', 'name', 'image_path'))})

    def delete(self, collection_id):
        abort_if_collection_not_found(collection_id)
        session = db_session.create_session()
        collection = session.query(Collection).get(collection_id)
        session.delete(collection)
        session.commit()
        return jsonify({'success': 'OK'})


class CollectionListResource(Resource):
    def get(self):
        session = db_session.create_session()
        collections = session.query(Collection).all()
        return jsonify({'collections': [item.to_dict(only=('id', 'name')) for item in collections]})

    def post(self):
        args = collection_parser.parse_args()
        session = db_session.create_session()
        collection = Collection(
            name=args['name'],
            image_path=args['image_path']
        )
        session.add(collection)
        session.commit()
        return jsonify({'id': collection.id}), 201


class NFTResource(Resource):
    def get(self, nft_id):
        abort_if_nft_not_found(nft_id)
        session = db_session.create_session()
        nft = session.query(NFT).get(nft_id)
        return jsonify({'nft': nft.to_dict(only=('id', 'name', 'rarity', 'image_path'))})

    def delete(self, nft_id):
        abort_if_nft_not_found(nft_id)
        session = db_session.create_session()
        nft = session.query(NFT).get(nft_id)
        session.delete(nft)
        session.commit()
        return jsonify({'success': 'OK'})


class NFTListResource(Resource):
    def get(self):
        session = db_session.create_session()
        nfts = session.query(NFT).all()
        return [{'id': nft.id,
                 'name': nft.name,
                 'rarity': nft.rarity,
                 'image_path': nft.image_path,
                 'collection_id': nft.collection_id} for nft in nfts], 200

    def post(self):
        args = nft_parser.parse_args()
        session = db_session.create_session()

        collection = session.query(Collection).filter(Collection.id == args['collection_id']).first()
        if not collection:
            return {'message': 'Collection not found.'}, 404

        if session.query(NFT).filter(NFT.name == args['name']).first():
            return {'message': 'NFT with this name already exists.'}, 400

        new_nft = NFT(
            name=args['name'],
            rarity=args['rarity'],
            image_path=args['image_path'],
            collection_id=args['collection_id']
        )

        session.add(new_nft)
        session.commit()

        return {'id': new_nft.id,
                'name': new_nft.name,
                'rarity': new_nft.rarity,
                'image_path': new_nft.image_path,
                'collection_id': new_nft.collection_id}, 201


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

