from . import db_session
from flask import jsonify
from data.videos import Video
from flask_restful import abort, Resource


def abort_if_video_not_found(video_id):
    session = db_session.create_session()
    video = session.query(Video).get(video_id)
    if not video:
        abort(404, message=f"Video {video_id} not found")


class VideosResource(Resource):
    def get(self, video_id):
        abort_if_video_not_found(video_id)
        session = db_session.create_session()
        video = session.query(Video).get(video_id)
        return jsonify({'video': video.to_dict()})


class VideoListResource(Resource):
    def get(self):
        session = db_session.create_session()
        video = session.query(Video).all()
        return jsonify({'video': [item.to_dict() for item in video]})
