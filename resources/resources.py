import pprint
from flask_restful import reqparse, abort, Resource
from data.databaseee import User, Collection, NFT, TradeRequests
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
            return ne_norm_list  # ну он не ненормальный список возрващвет, а уже нормальный, ну кароче переменная такая


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


def abort_if_trade_not_found(trade_id):
    session = db_session.create_session()
    user = session.query(TradeRequests).get(trade_id)
    if not user:
        abort(404, message=f"Trade {trade_id} not found")


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
        user.all_chances_to_default(session)
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
            for nft_name, nft_rarity, nft_image, r, sr, e, m, l, h, s, d, t in zip(nft_names, nft_rarities, nft_images,
                                                                                   rs, srs, es, ms, ls, hs, ss, ds, ts):
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

                    q = ["rare", "super_rare", "epic", "mythic", "legendary"]
                    nft_brawler_rarities = []
                    for i, el in enumerate([r, sr, e, m, l]):
                        if el:
                            nft_brawler_rarities.append(q[i])

                    q = ["healer", "damage_dealer", "sniper", "tank"]
                    nft_brawler_classes = []
                    for i, el in enumerate([h, s, d, t]):
                        if el:
                            nft_brawler_classes.append(q[i])
                    # Создание NFT с именем файла
                    nft = NFT(name=nft_name, rarity=nft_rarity, image_path=nft_file_name,
                              classes_as_brawler=" ".join(nft_brawler_classes),
                              rarities_as_brawler=" ".join(nft_brawler_rarities))
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
        try:
            print(1)
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
            click = user.click_count
            db_sess.merge(user)
            db_sess.commit()

            rarity_percents = {"rare": user.rare, "super_rare": user.super_rare, "epic": user.epic, "mythic": user.mythic,
                               "legendary": user.legendary, "": user.none}
            rarity_strike = {"rare": user.rare_s, "super_rare": user.super_rare_s, "epic": user.epic_s,
                             "mythic": user.mythic_s, "legendary": user.legendary_s, "": user.none_s}
            _rarity = random.choices(list(rarity_percents.keys()), weights=list(rarity_percents.values()))[0]
            print("выпала редкость:", _rarity)

            rarity_percents, rarity_strike = Brawlers.chance_rarity_changer(_rarity, rarity_percents, rarity_strike)
            user.RARITY_r_s(rarity_percents, rarity_strike, db_sess)
            response_data = None

            if _rarity:
                rarity_percents_br = {"rare": user.rare_br, "super_rare": user.super_rare_br, "epic": user.epic_br,
                                      "mythic": user.mythic_br, "legendary": user.legendary_br}
                rarity_strike_br = {"rare": user.rare_s_br, "super_rare": user.super_rare_s_br, "epic": user.epic_s_br,
                                    "mythic": user.mythic_s_br, "legendary": user.legendary_s_br}

                i_cant_be_r = []
                while True:
                    _rarity_as_br = \
                    random.choices(list(rarity_percents_br.keys()), weights=list(rarity_percents_br.values()))[0]
                    if _rarity_as_br in i_cant_be_r:
                        continue
                    this_rarity_rarity_nfts = db_sess.query(NFT).filter(NFT.rarity == _rarity,
                                                                        NFT.collection_id == collection_id,
                                                                        NFT.rarities_as_brawler.like(f"%{_rarity_as_br}%")).all()
                    if len(i_cant_be_r) == 5:
                        break
                    if not this_rarity_rarity_nfts:
                        i_cant_be_r.append(_rarity)
                        continue
                    rarity_percents_br, rarity_strike_br = Brawlers.chance_rarity_as_brawler_changer(_rarity_as_br,
                                                                                                     rarity_percents_br,
                                                                                                     rarity_strike_br)
                    user.BRAWLER_r_s(rarity_percents_br, rarity_strike_br, db_sess)
                    classes_percent = {"healer": user.healer, "damage_dealer": user.damage_dealer, "sniper": user.sniper,
                                       "tank": user.tank}
                    classes_strike = {"healer": user.healer_s, "damage_dealer": user.damage_dealer_s,
                                      "sniper": user.sniper_s,
                                      "tank": user.tank_s}
                    i_cant_be_c = []
                    while True:
                        _class = random.choices(list(classes_percent.keys()), weights=list(classes_percent.values()))[0]
                        if _class in i_cant_be_c:
                            continue
                        this_rarity_rarity_class_nfts = list(
                            filter(lambda _nft: _class in _nft.classes_as_brawler, this_rarity_rarity_nfts))
                        if not this_rarity_rarity_class_nfts:
                            i_cant_be_c.append(_class)
                            continue
                        if len(i_cant_be_c) == 4:
                            break
                        classes_percent, classes_strike = Brawlers.chance_class_changer(_class, classes_percent,
                                                                                        classes_strike)
                        user.CLASS_r_s(classes_percent, classes_strike, db_sess)
                        _nft_ = random.choices(this_rarity_rarity_class_nfts)[0]
                        inventory_path = f".users_json/{user.email}.json"
                        if os.path.exists(inventory_path):
                            with open(inventory_path, "r", encoding="utf8") as user_json:
                                inventory_data = json.load(user_json)
                        else:
                            inventory_data = {}
                        this_nft_id_list = inventory_data.get(str(_nft_.id), [])
                        this_nft_id_list.append({"rarity": _rarity_as_br, "brawler": _class})
                        inventory_data[str(_nft_.id)] = this_nft_id_list
                        with open(inventory_path, "w") as user_json:
                            json.dump(inventory_data, user_json)
                        print(2)
                        print(this_nft_id_list)
                        response_data = {'click_count': user.click_count,
                                         'nft_received': {
                                             "id": _nft_.id,
                                             "name": _nft_.name,
                                             "rarity": _nft_.rarity}}
                        break
                    break
            db_sess.close()
            return {"click_count": click, "response_data": None}, 200
        except Exception as e:
            print(e)


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


class TradingListResourse(Resource):
    def get(self):
        session = db_session.create_session()

        # Получаем все запросы на торговлю с информацией о NFT
        trade_requests = session.query(TradeRequests).all()

        response_data = []
        for i in trade_requests:
            print(i.id_nft)
            nft = session.query(NFT).filter(NFT.id == i.id_nft).first()
            if nft:
                response_data.append({
                    "trade_id": i.id,
                    'user_email': i.user_email,
                    'id_nft': i.id_nft,
                    'brawler_class': i.brawler_class,
                    'brawler_rarity': i.brawler_rarity,
                    'cost': i.cost,
                    'nft_name': nft.name,
                    'nft_rarity': nft.rarity,
                    'image_path': f"uploads/{nft.collection_id}/nfts/{nft.image_path}"
                })
        print(response_data)

        return jsonify({'trade_post': response_data})

    def post(self):
        data = request.get_json()

        if not data or 'user_email' not in data or 'nft' not in data or 'cost' not in data:
            return {'message': 'Пожалуйста, предоставьте email пользователя, NFT и стоимость'}, 400

        user_email = data.get('user_email')
        nft = data.get('nft')
        cost = data.get('cost')

        if int(cost) < 1:
            return {'message': 'Пожалуйста, введите корректную стоимость'}, 400

        session = db_session.create_session()
        user = session.query(User).filter(User.email == user_email).first()

        if not user:
            return {'message': 'Пользователь не найден'}, 404

        user_inventory_path = f"./users_jsons/{user_email}.json"

        if os.path.exists(user_inventory_path):
            with open(user_inventory_path, "r") as user_json:
                inventory_data = json.load(user_json)

            # Извлекаем ID и характеристики из строки
            nft_parts = nft.split()  # Разделяем строку на части
            nft_id = nft_parts[0]  # ID NFT
            brawler_class = nft_parts[2]  # Класс бравлера
            brawler_rarity = nft_parts[1]  # Редкость бравлера

            # Удаляем NFT из инвентаря по ID и характеристикам
            if nft_id in inventory_data:
                item_found = False

                for item in inventory_data[nft_id]:
                    if item['brawler'] == brawler_class and item['rarity'] == brawler_rarity:
                        inventory_data[nft_id].remove(item)
                        item_found = True
                        break

                if not item_found:
                    return {'message': 'NFT с заданными характеристиками не найден в инвентаре пользователя'}, 404
            else:
                return {'message': 'NFT не найден в инвентаре пользователя'}, 404

            with open(user_inventory_path, "w") as user_json:
                json.dump(inventory_data, user_json)

            # Создаем новый запрос на торговлю
            trade_request = TradeRequests(
                user_email=user_email,
                id_nft=int(nft_id),
                brawler_class=brawler_class,
                brawler_rarity=brawler_rarity,
                cost=int(cost)
            )

            session.add(trade_request)
            session.commit()

            return {'message': 'Запрос на торговлю успешно создан'}, 201


class TradingResourse(Resource):
    def get(self, trade_id):
        abort_if_trade_not_found(trade_id)
        session = db_session.create_session()
        news = session.query(TradeRequests).get(trade_id)
        return jsonify({'news': news.to_dict(
            only=('title', 'content', 'user_id', 'is_private'))})

    def post(self, trade_id, buyer_email):
        session = db_session.create_session()


        # Получаем торговый запрос по ID
        trade_request = session.query(TradeRequests).get(trade_id)

        if not trade_request:
            return {'message': 'Торговый запрос не найден'}, 404

        buyer = session.query(User).filter(User.email == buyer_email).first()

        if not buyer:
            return {'message': 'Покупатель не найден'}, 404

        # Проверяем наличие средств у покупателя
        if buyer.figli_coins < trade_request.cost:
            return {'message': 'Недостаточно средств для покупки'}, 400

        # Списываем средства с покупателя и переводим продавцу (предполагается, что seller_email хранится в trade_request)
        seller = session.query(User).filter(User.email == trade_request.user_email).first()

        buyer.figli_coins -= trade_request.cost
        seller.figli_coins += trade_request.cost

        # Добавляем NFT в инвентарь покупателя с характеристиками
        nft_data = {
            "rarity": trade_request.brawler_rarity,
            "brawler": trade_request.brawler_class
        }

        buyer_inventory_path = f"./users_jsons/{buyer_email}.json"

        if os.path.exists(buyer_inventory_path):
            with open(buyer_inventory_path, "r") as buyer_json:
                buyer_inventory_data = json.load(buyer_json)

            if str(trade_request.id_nft) not in buyer_inventory_data:
                buyer_inventory_data[str(trade_request.id_nft)] = []  # Инициализируем список для нового NFT

            buyer_inventory_data[str(trade_request.id_nft)].append(nft_data)  # Добавляем характеристики NFT в инвентарь

            with open(buyer_inventory_path, "w") as buyer_json:
                json.dump(buyer_inventory_data, buyer_json)

        # Удаляем торговый запрос после завершения сделки
        session.delete(trade_request)

        # Сохраняем изменения в базе данных
        session.commit()

        return {'message': 'Успешная покупка'}, 201
