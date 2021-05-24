import json
from . import db_session
from flask import jsonify
from data.users import User
from data.videos import Video
from flask_restful import abort, Resource
from flask_login import current_user


def abort_if_video_not_found(video_id):
    """Возвращает ошибку 404 если видео не найдено"""
    session = db_session.create_session()
    video = session.query(Video).get(video_id)
    if not video:
        abort(404, message=f"Cassette {video_id} not found")


def abort_if_user_not_authenticated():
    """Возвращает ошибку 403 если пользователь не аутентифицирован"""
    if not current_user.is_authenticated:
        abort(403, message=f"User is not authenticated")


class LikeResource(Resource):
    """Создает ресурс API для работы с добавлением видео в любимые"""

    def post(self, video_id):
        """Добавляет видео в любимые"""
        abort_if_user_not_authenticated()
        abort_if_video_not_found(video_id)
        session = db_session.create_session()
        video = session.query(Video).get(video_id)
        if video.author == current_user.id:
            abort(403, message=f"User {current_user.id} has no permission")
        user = session.query(User).get(current_user.id)
        likes = json.loads(user.likes)
        if video_id in likes:
            abort(403, message=f"Cassette {video_id} already in likes")
        likes.append(video_id)
        user.likes = json.dumps(likes)
        video.likes += 1
        session.commit()
        return jsonify({'success': 'OK'})


class NotLikeResource(Resource):
    """Создает ресурс API для работы с удалением видео из любимых"""

    def post(self, video_id):
        """Удаляет видео из любимых"""
        abort_if_user_not_authenticated()
        abort_if_video_not_found(video_id)
        session = db_session.create_session()
        video = session.query(Video).get(video_id)
        if video.author == current_user.id:
            abort(403, message=f"User {current_user.id} has no permission")
        user = session.query(User).get(current_user.id)
        likes = json.loads(user.likes)
        if video_id not in likes:
            abort(403, message=f"Cassette {video_id} already in likes")
        del likes[likes.index(video_id)]
        user.likes = json.dumps(likes)
        video.likes -= 1
        session.commit()
        return jsonify({'success': 'OK'})
