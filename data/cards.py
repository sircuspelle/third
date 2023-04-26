import datetime

import sqlalchemy
from sqlalchemy import orm

from data.db_session import SqlAlchemyBase


class Card(SqlAlchemyBase):
    __tablename__ = 'cards'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    region = sqlalchemy.Column(sqlalchemy.String, default='Санкт-Петербург')
    place = sqlalchemy.Column(sqlalchemy.Integer)
    longest = sqlalchemy.Column(sqlalchemy.String)
    loyality = sqlalchemy.Column(sqlalchemy.String, default='0')
    loyality_counter = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    points_count = sqlalchemy.Column(sqlalchemy.Integer)
    changed_at = sqlalchemy.Column(sqlalchemy.Date, default=datetime.datetime.now)
    map = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    creator = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey("users.id"), default=1)
    creator_obj = orm.relationship('User')


class Card_Page(SqlAlchemyBase):
    __tablename__ = 'small_cards'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    txt = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    picture = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    mother = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("cards.id"), default=1)
    mother_obj = orm.relationship('Card')