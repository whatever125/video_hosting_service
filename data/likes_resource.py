import json
from . import db_session
from flask import jsonify
from data.users import User
from data.videos import Video
from flask_restful import abort, Resource
from flask_login import current_user


def abort_if_video_not_found(video_id):
    session = db_session.create_session()
    video = session.query(Video).get(video_id)
    if not video:
        abort(404, message=f"Video {video_id} not found")


def abort_if_user_not_authenticated():
    if not current_user.is_authenticated:
        abort(403, message=f"User is not authenticated")


class LikeResource(Resource):
    def post(self, video_id):
        abort_if_user_not_authenticated()
        abort_if_video_not_found(video_id)
        session = db_session.create_session()
        video = session.query(Video).get(video_id)
        if video.author == current_user.id:
            abort(403, message=f"User {current_user.id} has no permission")
        user = session.query(User).get(current_user.id)
        likes = json.loads(user.likes)
        likes.append(video_id)
        user.likes = json.dumps(likes)
        video.likes += 1
        try:
            dislikes = json.loads(user.dislikes)
            del dislikes[dislikes.index(video_id)]
            user.dislikes = json.dumps(dislikes)
            video.dislikes -= 1
        except ValueError:
            pass
        session.commit()
        return jsonify({'success': 'OK'})


class DislikeResource(Resource):
    def post(self, video_id):
        abort_if_user_not_authenticated()
        abort_if_video_not_found(video_id)
        session = db_session.create_session()
        video = session.query(Video).get(video_id)
        if video.author == current_user.id:
            abort(403, message=f"User {current_user.id} has no permission")
        user = session.query(User).get(current_user.id)
        dislikes = json.loads(user.dislikes)
        dislikes.append(video_id)
        user.dislikes = json.dumps(dislikes)
        video.dislikes += 1
        try:
            likes = json.loads(user.likes)
            del likes[likes.index(video_id)]
            user.likes = json.dumps(likes)
            video.likes -= 1
        except ValueError:
            pass
        session.commit()
        return jsonify({'success': 'OK'})


class NotLikeResource(Resource):
    def post(self, video_id):
        abort_if_user_not_authenticated()
        abort_if_video_not_found(video_id)
        session = db_session.create_session()
        video = session.query(Video).get(video_id)
        if video.author == current_user.id:
            abort(403, message=f"User {current_user.id} has no permission")
        user = session.query(User).get(current_user.id)
        try:
            likes = json.loads(user.likes)
            del likes[likes.index(video_id)]
            user.likes = json.dumps(likes)
            video.likes -= 1
        except ValueError:
            pass
        try:
            dislikes = json.loads(user.dislikes)
            del dislikes[dislikes.index(video_id)]
            user.dislikes = json.dumps(dislikes)
            video.dislikes -= 1
        except ValueError:
            pass
        session.commit()
        return jsonify({'success': 'OK'})
