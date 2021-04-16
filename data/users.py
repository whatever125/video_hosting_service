import sqlalchemy
from flask_login import UserMixin
from .db_session import SqlAlchemyBase
from datetime import datetime


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    login = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    followers = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)
    haters = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)
    subscriptions = sqlalchemy.Column(sqlalchemy.String, nullable=False, default='[]')
    unsubscriptions = sqlalchemy.Column(sqlalchemy.String, nullable=False, default='[]')
    likes = sqlalchemy.Column(sqlalchemy.String, nullable=False, default='[]')
    dislikes = sqlalchemy.Column(sqlalchemy.String, nullable=False, default='[]')
    datetime = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, default=datetime.utcnow)
