from flask import Flask, render_template, url_for
from data.videos import Video
from data.users import User
from data import db_session
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db_sess.query(User).get(user_id)


@app.route('/')
@app.route('/index')
def index():
    all_videos = db_sess.query(Video).all()
    last_videos = all_videos[len(all_videos) - 3:][::-1]
    best_videos = sorted(all_videos, key=lambda x: -x.likes)[:3]
    worst_videos = sorted(all_videos, key=lambda x: -x.dislikes)[:3]
    params = {
        'title': 'Video Hosting',
        'last_videos': last_videos,
        'best_videos': best_videos,
        'worst_videos': worst_videos,
        'db_sess': db_sess,
        'User': User,
        'Video': Video
    }
    return render_template('index.html', **params)


@app.route('/video/<video_id>')
def video(video_id):
    video_id = int(video_id)
    current_video = db_sess.query(Video).filter(Video.id == video_id).first()
    title = current_video.title
    author_id = current_video.author
    author = db_sess.query(User).filter(User.id == author_id).first()
    params = {
        'title': f'{title} - {author.name} {author.surname}',
        'current_video': current_video,
        'video_id': video_id,
        'video_src': url_for("static", filename=f'vid/{video_id}.mp4'),
        'author': author
    }
    return render_template('video.html', **params)


def main():
    app.run()


if __name__ == '__main__':
    db_session.global_init("db/hosting.sql")
    db_sess = db_session.create_session()
    main()
