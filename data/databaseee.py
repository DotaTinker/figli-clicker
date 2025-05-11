import datetime
import sqlalchemy
from data.db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.orm import relationship


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

    def to_dict(self, only=None):
        data = {
            'id_nft': self.id_nft,
            'user_email': self.user_email,
            'brawler_class': self.brawler_class,
            'brawler_rarity': self.brawler_rarity,
            "cost": self.cost
        }
        if only:
            return {key: data[key] for key in only if key in data}
        return data