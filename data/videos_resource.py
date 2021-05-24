from . import db_session
from flask import jsonify
from data.videos import Video
from flask_restful import abort, Resource


def abort_if_video_not_found(video_id):
    """Возвращает ошибку 404 если видео не найдено"""
    session = db_session.create_session()
    video = session.query(Video).get(video_id)
    if not video:
        abort(404, message=f"Video {video_id} not found")


class VideosResource(Resource):
    """Создает ресурс API для работы с видео"""

    def get(self, video_id):
        """Возвращает информацию о видео"""
        abort_if_video_not_found(video_id)
        session = db_session.create_session()
        video = session.query(Video).get(video_id)
        return jsonify({'video': video.to_dict()})


class VideoListResource(Resource):
    """Создает ресурс API для работы со всеми видео"""

    def get(self):
        """Возвращает информацию о всех видео"""
        session = db_session.create_session()
        video = session.query(Video).all()
        return jsonify({'video': [item.to_dict() for item in video]})
