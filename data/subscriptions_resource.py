import json
from . import db_session
from flask import jsonify
from data.users import User
from flask_restful import abort, Resource
from flask_login import current_user


def abort_if_user_not_found(user_id):
    """Возвращает ошибку 404 если пользователь не найден"""
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


def abort_if_user_not_authenticated():
    """Возвращает ошибку 403 если пользователь не аутентифицирован"""
    if not current_user.is_authenticated:
        abort(403, message=f"User is not authenticated")


class FollowResource(Resource):
    """Создает ресурс API для работы с подпиской на пользователя"""

    def post(self, user_id):
        """Подписывает на пользователя"""
        abort_if_user_not_authenticated()
        abort_if_user_not_found(user_id)
        if user_id == current_user.id:
            abort(403, message=f"User {current_user.id} has no permission")
        session = db_session.create_session()
        user = session.query(User).get(current_user.id)
        subscriptions = json.loads(user.subscriptions)
        if user_id in subscriptions:
            abort(403, message=f'User {user_id} already in subscriptions')
        subscriptions.append(user_id)
        user.subscriptions = json.dumps(subscriptions)
        author = session.query(User).get(user_id)
        author.followers += 1
        session.commit()
        return jsonify({'success': 'OK'})


class NotFollowResource(Resource):
    """Создает ресурс API для работы с отпиской от пользователя"""

    def post(self, user_id):
        """Отписывает от пользователя"""
        abort_if_user_not_authenticated()
        abort_if_user_not_found(user_id)
        if user_id == current_user.id:
            abort(403, message=f"User {current_user.id} has no permission")
        session = db_session.create_session()
        user = session.query(User).get(current_user.id)
        subscriptions = json.loads(user.subscriptions)
        if user_id not in subscriptions:
            abort(403, message=f'User {user_id} not in subscriptions')
        del subscriptions[subscriptions.index(user_id)]
        user.subscriptions = json.dumps(subscriptions)
        author = session.query(User).get(user_id)
        author.followers -= 1
        session.commit()
        return jsonify({'success': 'OK'})
