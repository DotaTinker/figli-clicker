from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase


class Collection(SqlAlchemyBase):
    __tablename__ = 'collections'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    image_path = Column(String, nullable=False)  # Путь к изображению коллекции
    nfts = relationship("NFT", back_populates="collection")


class NFT(SqlAlchemyBase):
    __tablename__ = 'nfts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    rarity = Column(String, nullable=False)
    image_path = Column(String, nullable=False)  # Путь к изображению NFT
    collection_id = Column(Integer, ForeignKey('collections.id'))
    collection = relationship("Collection", back_populates="nfts")
