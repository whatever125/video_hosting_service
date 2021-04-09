import sqlalchemy
from .db_session import SqlAlchemyBase


class Video(SqlAlchemyBase):
    __tablename__ = 'videos'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, nullable=False)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    author = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("users.id"), nullable=False)
    likes = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    dislikes = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    datetime = sqlalchemy.Column(sqlalchemy.String, nullable=True)
