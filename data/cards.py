import datetime

import sqlalchemy
from sqlalchemy import orm

from data.db_session import SqlAlchemyBase


class Card(SqlAlchemyBase):
    __tablename__ = 'cards'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    region = sqlalchemy.Column(sqlalchemy.String)
    place = sqlalchemy.Column(sqlalchemy.Integer)
    longest = sqlalchemy.Column(sqlalchemy.String)
    changed_at = sqlalchemy.Column(sqlalchemy.Date, default=datetime.datetime.now)
    map = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    txts = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    medias = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    creator = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey("users.id"), default=1)
    leader_obj = orm.relationship('User')