from . import db_session
from flask import jsonify
from data.users import User
from .users_arg_parser import parser
from flask_restful import abort, Resource


def abort_if_user_not_found(user_id):
    """Возвращает ошибку 404 если пользователь не найден"""
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


class UsersResource(Resource):
    """Создает ресурс API для работы с пользователем"""

    def get(self, user_id):
        """Возвращает информацию о пользователе"""
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict(
            only=('id', 'login', 'name', 'surname', 'followers', 'datetime'))})


class UserListResource(Resource):
    """Создает ресурс API для работы с пользователями"""

    def get(self):
        """Возвращает информацию о всех пользователях"""
        session = db_session.create_session()
        user = session.query(User).all()
        return jsonify({'user': [item.to_dict(
            only=('id', 'login', 'name', 'surname', 'followers', 'datetime')) for item in user]})

    def post(self):
        """Добавляет новго пользователя"""
        args = parser.parse_args()
        db_sess = db_session.create_session()
        user = User()
        user.login = args['login']
        user.password = args['password']
        user.name = args['name']
        user.surname = args['surname']
        db_sess.add(user)
        db_sess.commit()
        return jsonify({'success': 'OK'})
