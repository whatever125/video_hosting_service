import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime


class Video(SqlAlchemyBase, SerializerMixin):
    """Определяет таблицу с видео в базе данных"""
    __tablename__ = 'videos'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    author = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("users.id"), nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=False, default='')
    likes = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)
    datetime = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, default=datetime.utcnow)
