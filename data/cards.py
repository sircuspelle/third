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
    changed_at = sqlalchemy.Column(sqlalchemy.Date)
    map = sqlalchemy.Column(sqlalchemy.String)
    txts = sqlalchemy.Column(sqlalchemy.String)
    medias = sqlalchemy.Column(sqlalchemy.String)
    creator = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey("users.id"))
    leader_obj = orm.relationship('User')