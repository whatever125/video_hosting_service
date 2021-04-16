import json
from . import db_session
from flask import jsonify
from data.users import User
from flask_restful import abort, Resource
from flask_login import current_user


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


def abort_if_user_not_authenticated():
    if not current_user.is_authenticated:
        abort(403, message=f"User is not authenticated")


class FollowResource(Resource):
    def post(self, user_id):
        abort_if_user_not_authenticated()
        abort_if_user_not_found(user_id)
        if user_id == current_user.id:
            abort(403, message=f"User {current_user.id} has no permission")
        session = db_session.create_session()
        user = session.query(User).get(current_user.id)
        author = session.query(User).get(user_id)
        subscriptions = json.loads(user.subscriptions)
        subscriptions.append(user_id)
        user.subscriptions = json.dumps(subscriptions)
        author.followers += 1
        try:
            unsubscriptions = json.loads(user.unsubscriptions)
            del unsubscriptions[unsubscriptions.index(user_id)]
            user.unsubscriptions = json.dumps(unsubscriptions)
            author.haters -= 1
        except ValueError:
            pass
        session.commit()
        return jsonify({'success': 'OK'})


class UnfollowResource(Resource):
    def post(self, user_id):
        abort_if_user_not_authenticated()
        abort_if_user_not_found(user_id)
        if user_id == current_user.id:
            abort(403, message=f"User {current_user.id} has no permission")
        session = db_session.create_session()
        user = session.query(User).get(current_user.id)
        author = session.query(User).get(user_id)
        unsubscriptions = json.loads(user.unsubscriptions)
        unsubscriptions.append(user_id)
        user.unsubscriptions = json.dumps(unsubscriptions)
        author.haters += 1
        try:
            subscriptions = json.loads(user.subscriptions)
            del subscriptions[subscriptions.index(user_id)]
            user.subscriptions = json.dumps(subscriptions)
            author.followers -= 1
        except ValueError:
            pass
        session.commit()
        return jsonify({'success': 'OK'})


class NotFollowResource(Resource):
    def post(self, user_id):
        abort_if_user_not_authenticated()
        abort_if_user_not_found(user_id)
        if user_id == current_user.id:
            abort(403, message=f"User {current_user.id} has no permission")
        session = db_session.create_session()
        user = session.query(User).get(current_user.id)
        author = session.query(User).get(user_id)
        try:
            subscriptions = json.loads(user.subscriptions)
            del subscriptions[subscriptions.index(user_id)]
            user.subscriptions = json.dumps(subscriptions)
            author.followers -= 1
        except ValueError:
            pass
        try:
            unsubscriptions = json.loads(user.unsubscriptions)
            del unsubscriptions[unsubscriptions.index(user_id)]
            user.unsubscriptions = json.dumps(unsubscriptions)
            author.haters -= 1
        except ValueError:
            pass
        session.commit()
        return jsonify({'success': 'OK'})
