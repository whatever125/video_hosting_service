import os
import json
from flask import Flask, render_template, url_for, redirect, request
from data.videos import Video
from data.users import User
from data import db_session
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from data.login_form import LoginForm
from data.register_form import RegisterForm
from data.video_form import VideoForm
from flask_restful import reqparse, abort, Api, Resource
from data.users_resource import UsersResource, UserListResource

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)


@app.errorhandler(403)
def forbidden(e):
    params = {
        'title': 'Доступ запрещен',
        'authenticated': current_user.is_authenticated,
        'current_user': current_user
    }
    return render_template('403.html', **params), 403


@app.errorhandler(404)
def page_not_found(e):
    params = {
        'title': 'Страница не найдена',
        'authenticated': current_user.is_authenticated,
        'current_user': current_user
    }
    return render_template('404.html', **params), 404


@app.errorhandler(500)
def internal_server_error(e):
    params = {
        'title': 'Ошибка сервера',
        'authenticated': current_user.is_authenticated,
        'current_user': current_user
    }
    return render_template('500.html', **params), 500


@app.route('/')
@app.route('/index')
def index():
    all_videos = db_sess.query(Video).all()
    last_videos = all_videos[len(all_videos) - 3:][::-1]
    best_videos = sorted(all_videos, key=lambda x: -(x.likes - x.dislikes))[:3]
    worst_videos = sorted(all_videos, key=lambda x: x.likes - x.dislikes)[:3]
    params = {
        'title': 'Home page',
        'last_videos': last_videos,
        'best_videos': best_videos,
        'worst_videos': worst_videos,
        'db_sess': db_sess,
        'User': User,
        'Video': Video,
        'authenticated': current_user.is_authenticated,
        'current_user': current_user
    }
    return render_template('index.html', **params)


@login_manager.user_loader
def load_user(user_id):
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    params = {
        'title': 'Авторизация',
        'authenticated': current_user.is_authenticated,
        'current_user': current_user
    }
    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.login == form.login.data).first()
        if user and user.password == form.password.data:
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html',
                               message='Неправильный логин или пароль',
                               form=form, **params)
    return render_template('login.html', form=form, **params)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    params = {
        'title': 'Регистрация',
        'authenticated': current_user.is_authenticated,
        'current_user': current_user
    }
    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.login == form.login.data).all()
        if user:
            return render_template('register.html',
                                   message='Пользователь с таким логином уже существует',
                                   form=form, **params)
        if form.password.data != form.repeat_password.data:
            return render_template('register.html',
                                   message='Пароли не совпадают',
                                   form=form, **params)
        user = User()
        user.login = form.login.data
        user.password = form.password.data
        user.name = form.name.data
        user.surname = form.surname.data
        db_sess.add(user)
        db_sess.commit()
        login_user(user, remember=form.remember_me.data)
        return redirect('/')
    return render_template('register.html', form=form, **params)


@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        return redirect('/')
    else:
        return forbidden('')


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
        'author': author,
        'authenticated': current_user.is_authenticated,
        'current_user': current_user
    }
    return render_template('video.html', **params)


@app.route('/add_video', methods=['GET', 'POST'])
def add_video():
    if not current_user.is_authenticated:
        return forbidden('')
    form = VideoForm()
    params = {
        'title': 'Загрузка видео',
        'authenticated': current_user.is_authenticated,
        'current_user': current_user
    }
    if form.validate_on_submit():
        video_file = request.files['video']
        if not video_file.filename.lower().endswith('.mp4'):
            return render_template('add_video.html',
                                   message='Данный формат файла не поддерживается',
                                   form=form, **params)
        preview_file = request.files['preview']
        if not preview_file.filename.lower().endswith('.jpg'):
            return render_template('add_video.html',
                                   message='Данный формат файла не поддерживается',
                                   form=form, **params)
        video = Video()
        video.title = form.title.data
        video.description = '<br>'.join(form.description.data.split('\n'))
        video.author = current_user.id
        db_sess.add(video)
        db_sess.commit()
        video_file.save(os.path.join('static/vid', f'{video.id}.mp4'))
        preview_file.save(os.path.join('static/pre', f'{video.id}.jpg'))
        return redirect('/')
    return render_template('add_video.html', form=form, **params)


@app.route('/edit_video/<video_id>', methods=['GET', 'POST'])
def edit_video(video_id):
    form = VideoForm()
    video = db_sess.query(Video).filter(Video.id == video_id).first()
    if not current_user.is_authenticated or current_user.id != video.author:
        return forbidden('')
    params = {
        'title': 'Редактирование видео',
        'video': video,
        'description': '\n'.join(video.description.split('<br>')),
        'authenticated': current_user.is_authenticated,
        'current_user': current_user
    }
    if form.validate_on_submit():
        video_file = request.files['video']
        if not video_file.filename.lower().endswith('.mp4'):
            return render_template('edit_video.html',
                                   message='Данный формат файла не поддерживается',
                                   form=form, **params)
        preview_file = request.files['preview']
        if not preview_file.filename.lower().endswith('.jpg'):
            return render_template('edit_video.html',
                                   message='Данный формат файла не поддерживается',
                                   form=form, **params)
        video.title = form.title.data
        video.description = '<br>'.join(form.description.data.split('\n'))
        db_sess.commit()
        video_file.save(os.path.join('static/vid', f'{video.id}.mp4'))
        preview_file.save(os.path.join('static/pre', f'{video.id}.jpg'))
        return redirect('/')
    return render_template('edit_video.html', form=form, **params)


@app.route('/delete_video/<video_id>')
def delete_video(video_id):
    video = db_sess.query(Video).filter(Video.id == video_id).first()
    if current_user.id != video.author:
        return redirect('/')
    db_sess.delete(video)
    db_sess.commit()
    os.remove(os.path.join('static/vid', f'{video.id}.mp4'))
    os.remove(os.path.join('static/pre', f'{video.id}.jpg'))
    return redirect('/')


@app.route('/user/<user_id>')
def user(user_id):
    user_id = int(user_id)
    user = db_sess.query(User).filter(User.id == user_id).first()
    videos = db_sess.query(Video).filter(Video.author == user_id).all()[::-1]
    params = {
        'title': f'{user.name} {user.surname}',
        'user': user,
        'videos': [videos[i * 3:i * 3 + 3] for i in range(len(videos) // 3)] +
                  [videos[(len(videos) // 3) * 3:]],
        'authenticated': current_user.is_authenticated,
        'current_user': current_user
    }
    return render_template('user.html', **params)


@app.route('/like/<video_id>')
def like(video_id):
    if not current_user.is_authenticated:
        return forbidden('')
    print('like', video_id)
    return redirect(f'/video/{video_id}')


@app.route('/not_like/<video_id>')
def not_like(video_id):
    if not current_user.is_authenticated:
        return forbidden('')
    print('not_like', video_id)
    return ''


@app.route('/dislike/<video_id>')
def dislike(video_id):
    if not current_user.is_authenticated:
        return forbidden('')
    print('dislike', video_id)
    return ''


@app.route('/follow/<user_id>')
def follow(user_id):
    if not current_user.is_authenticated or current_user.id == user_id:
        return forbidden('')
    print('follow', user_id)
    return ''


@app.route('/not_follow/<user_id>')
def not_follow(user_id):
    if not current_user.is_authenticated or current_user.id == user_id:
        return forbidden('')
    print('not_follow', user_id)
    return ''


@app.route('/unfollow/<user_id>')
def unfollow(user_id):
    if not current_user.is_authenticated or current_user.id == user_id:
        return forbidden('')
    print('unfollow', user_id)
    return ''


def main():
    app.run()


if __name__ == '__main__':
    db_session.global_init("db/hosting.sql")
    db_sess = db_session.create_session()
    api.add_resource(UsersResource, '/api/users')
    api.add_resource(UserListResource, '/api/users/<int:user_id>')
    main()
