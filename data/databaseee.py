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
    image_path = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    collection_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('collections.id'))
    collection = relationship("Collection", back_populates="nfts")
