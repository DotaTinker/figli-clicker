import datetime
import sqlalchemy
from data.db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.orm import relationship
classes_persent = {"healer": 25, "damage_dealer": 25, "sniper": 25, "tank": 25}
classes_strike = {"healer": 0, "damage_dealer": 0, "sniper": 0, "tank": 0}
rarity_percents = {"rare": 1, "super_rare": 0.7, "epic": 0.5, "mythic": 0.25, "legendary": 0.04, "": 97.51}
rarity_strike = {"rare": 0, "super_rare": 0, "epic": 0, "mythic": 0, "legendary": 0, "": 0}
rarity_as_brawler_percents = {"rare": 48, "super_rare": 30, "epic": 16, "mythic": 5, "legendary": 1}
rarity_as_brawler_strike = {"rare": 0, "super_rare": 0, "epic": 0, "mythic": 0, "legendary": 0}


class User(SqlAlchemyBase, UserMixin):
    """id, user_name и email - уникальны.
        User_name используется для более лёгкого нахождения пользователей"""
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    user_name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    figli_coins = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    is_admin = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)
    click_count = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)
    # дальше идут шансы на редкости, серии выпадения редкостей, они могут быть пустыми т.к создаются
    # в тот момент, когда пользователь впервые зашёл в кликер, а значит, зарегался
    rare = sqlalchemy.Column(sqlalchemy.FLOAT, nullable=True)
    super_rare = sqlalchemy.Column(sqlalchemy.FLOAT, nullable=True)
    epic = sqlalchemy.Column(sqlalchemy.FLOAT, nullable=True)
    mythic = sqlalchemy.Column(sqlalchemy.FLOAT, nullable=True)
    legendary = sqlalchemy.Column(sqlalchemy.FLOAT, nullable=True)
    none = sqlalchemy.Column(sqlalchemy.FLOAT, nullable=True)
    rare_s = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    super_rare_s = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    epic_s = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    mythic_s = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    legendary_s = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    none_s = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    # шансы на редкость бравлеров и страйки
    rare_br = sqlalchemy.Column(sqlalchemy.FLOAT, nullable=True)
    super_rare_br = sqlalchemy.Column(sqlalchemy.FLOAT, nullable=True)
    epic_br = sqlalchemy.Column(sqlalchemy.FLOAT, nullable=True)
    mythic_br = sqlalchemy.Column(sqlalchemy.FLOAT, nullable=True)
    legendary_br = sqlalchemy.Column(sqlalchemy.FLOAT, nullable=True)
    rare_s_br = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    super_rare_s_br = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    epic_s_br = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    mythic_s_br = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    legendary_s_br = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    # далее шансы на классы и серии выпадений классов
    damage_dealer = sqlalchemy.Column(sqlalchemy.FLOAT, nullable=True)
    sniper = sqlalchemy.Column(sqlalchemy.FLOAT, nullable=True)
    tank = sqlalchemy.Column(sqlalchemy.FLOAT, nullable=True)
    healer = sqlalchemy.Column(sqlalchemy.FLOAT, nullable=True)
    damage_dealer_s = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    sniper_s = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    tank_s = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    healer_s = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    def __repr__(self):
        return (f"""{self.id}, {self.name}, {self.user_name}, {self.email}, {self.hashed_password}, 
                {self.figli_coins}, {self.modified_date}, {self.is_admin}""")

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        return True

    def to_dict(self, only=None):
        data = {
            'id': self.id,
            'name': self.name,
            'user_name': self.user_name,
            'email': self.email
        }
        if only:
            return {key: data[key] for key in only if key in data}
        return data

    def all_chances_to_default(self, session):
        self.RARITY_r_s(rarity_percents, rarity_strike, session)
        self.BRAWLER_r_s(rarity_as_brawler_percents, rarity_as_brawler_strike, session)
        self.CLASS_r_s(classes_persent, classes_strike, session)

    def RARITY_r_s(self, r_p, r_s, session):
        for k, v in r_p.items():
            if k == "rare":
                self.rare = v
            elif k == "super_rare":
                self.super_rare = v
            elif k == "epic":
                self.epic = v
            elif k == "mythic":
                self.mythic = v
            elif k == "legendary":
                self.legendary = v
            else:
                self.none = v
            session.commit()

        for k, v in r_s.items():
            if k == "rare":
                self.rare_s = v
            elif k == "super_rare":
                self.super_rare_s = v
            elif k == "epic":
                self.epic_s = v
            elif k == "mythic":
                self.mythic_s = v
            elif k == "legendary":
                self.legendary_s = v
            else:
                self.none_s = v
            session.commit()

    def BRAWLER_r_s(self, r_p, r_s, session):
        for k, v in r_p.items():
            if k == "rare":
                self.rare_br = v
            elif k == "super_rare":
                self.super_rare_br = v
            elif k == "epic":
                self.epic_br = v
            elif k == "mythic":
                self.mythic_br = v
            elif k == "legendary":
                self.legendary_br = v
            session.commit()

        for k, v in r_s.items():
            if k == "rare":
                self.rare_s_br = v
            elif k == "super_rare":
                self.super_rare_s_br = v
            elif k == "epic":
                self.epic_s_br = v
            elif k == "mythic":
                self.mythic_s_br = v
            elif k == "legendary":
                self.legendary_s_br = v
            session.commit()

    def CLASS_r_s(self, c_p, c_s, session):
        for k, v in c_p.items():
            if k == "healer":
                self.healer = v
            if k == "tank":
                self.tank = v
            if k == "sniper":
                self.sniper = v
            if k == "damage_dealer":
                self.damage_dealer = v
            session.commit()
        for k, v in c_s.items():
            if k == "healer":
                self.healer_s = v
            if k == "tank":
                self.tank_s = v
            if k == "sniper":
                self.sniper_s = v
            if k == "damage_dealer":
                self.damage_dealer_s = v
            session.commit()


class Collection(SqlAlchemyBase):
    """Имя коллекции уникально и используется для записи в json файл о пользователе,
        это упрощает переименование и удаление коллекций, т.к id - автоинкрементен"""
    __tablename__ = 'collections'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    image_path = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    nfts = relationship("NFT", back_populates="collection")


class NFT(SqlAlchemyBase):
    """Имя nft уникально и используется для записи в json файл о пользователе,
        это упрощает переименование и удаление nft, т.к id - автоинкрементен"""
    __tablename__ = 'nfts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    rarity = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    rarities_as_brawler = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    classes_as_brawler = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    image_path = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    collection_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('collections.id'))
    collection = relationship("Collection", back_populates="nfts")


class TradeRequests(SqlAlchemyBase):
    """Тут храгятся все запросы на торговлю от игроков"""
    __tablename__ = 'TradeForFigli'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_email = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    id_nft = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    brawler_class = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    brawler_rarity = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    cost = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
