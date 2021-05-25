import os
import json
from passlib.context import CryptContext
from PIL import Image
from flask import Flask, render_template, url_for, redirect, request, send_from_directory
from flask_login import LoginManager, login_user, current_user, logout_user
from flask_restful import Api
from data import db_session
from data.videos import Video
from data.users import User
from data.login_form import LoginForm
from data.register_form import RegisterForm
from data.video_form import VideoForm
from data.users_resource import UsersResource, UserListResource
from data.videos_resource import VideosResource, VideoListResource
from data.likes_resource import LikeResource, NotLikeResource
from data.subscriptions_resource import FollowResource, NotFollowResource

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=30000
)


@app.route('/favicon.ico')
def favicon():
    """Возвращает кастомную иконку страницы в браузере"""
    return send_from_directory(os.path.join(app.root_path, 'static/img'),
                               'vhs.ico', mimetype='image/vnd.microsoft.icon')


@app.errorhandler(403)
def forbidden(e):
    """Возвращает кастомную страницу ошибки 403"""
    params = {
        'title': 'Доступ запрещен',
        'message': 'Похоже, у вас нет доступа к этой странице ¯\\_(ツ)_/¯',
        'authenticated': current_user.is_authenticated,
        'current_user': current_user
    }
    return render_template('error.html', **params), 403


@app.errorhandler(404)
def page_not_found(e):
    """Возвращает кастомную страницу ошибки 404"""
    params = {
        'title': 'Страница не найдена',
        'message': 'Похоже, мы не можем найти нужную вам страницу ¯\\_(ツ)_/¯',
        'authenticated': current_user.is_authenticated,
        'current_user': current_user
    }
    return render_template('error.html', **params), 404


@app.errorhandler(405)
def method_not_allowed(e):
    """Возвращает кастомную страницу ошибки 405"""
    params = {
        'title': 'Метод не разрешен',
        'message': 'Похоже, этот метод не разрешен ¯\\_(ツ)_/¯',
        'authenticated': current_user.is_authenticated,
        'current_user': current_user
    }
    return render_template('error.html', **params), 405


@app.errorhandler(500)
def internal_server_error(e):
    """Возвращает кастомную страницу ошибки 500"""
    params = {
        'title': 'Ошибка сервера',
        'message': 'Похоже, на сервере произошла непредвиденная ошибка ¯\\_(ツ)_/¯',
        'authenticated': current_user.is_authenticated,
        'current_user': current_user
    }
    return render_template('error.html', **params), 500


@app.route('/')
@app.route('/index')
def index():
    """Возвращает домашнюю страницу"""
    all_videos = db_sess.query(Video).all()
    if len(all_videos) > 3:
        last_videos = all_videos[len(all_videos) - 3:][::-1]
    else:
        last_videos = all_videos[::-1]
    best_videos = sorted(all_videos, key=lambda x: -x.likes)[:3]
    underrated_videos = list(filter(lambda x: x.likes == 0, all_videos))
    if len(underrated_videos) > 3:
        underrated_videos = underrated_videos[len(underrated_videos) - 3:][::-1]
    else:
        underrated_videos = underrated_videos[::-1]
    params = {
        'title': 'Video Hosting Service',
        'last_videos': last_videos,
        'best_videos': best_videos,
        'underrated_videos': underrated_videos,
        'user': user,
        'db_sess': db_sess,
        'User': User,
        'Video': Video,
        'authenticated': current_user.is_authenticated,
        'current_user': current_user
    }
    return render_template('index.html', **params)


@login_manager.user_loader
def load_user(user_id):
    """Возвращает пользователя"""
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Возвращает страницу авторизации и авторизует пользователя"""
    if current_user.is_authenticated:
        return forbidden('')
    form = LoginForm()
    params = {
        'title': 'Авторизация',
        'authenticated': current_user.is_authenticated,
        'current_user': current_user
    }
    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.login == form.login.data).first()
        if user and pwd_context.verify(form.password.data, user.password):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html',
                               message='Неправильный логин или пароль',
                               form=form, **params)
    return render_template('login.html', form=form, **params)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Возвращает страницу регистрации и регистрирует пользователя"""
    if current_user.is_authenticated:
        return forbidden('')
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
        user.password = pwd_context.hash(form.password.data)
        user.name = form.name.data
        user.surname = form.surname.data
        db_sess.add(user)
        db_sess.commit()
        login_user(user, remember=form.remember_me.data)
        return redirect('/')
    return render_template('register.html', form=form, **params)


@app.route('/logout')
def logout():
    """
    Производит выход пользователя из системы, возвращает домашнюю страницу.
    Если пользователь не авторизован, возвращает страницу ошибки 403
    """
    if current_user.is_authenticated:
        logout_user()
        return redirect('/')
    else:
        return forbidden('')


@app.route('/video/<int:video_id>')
def video(video_id):
    """Возвращает страницу с видео"""
    current_video = db_sess.query(Video).get(video_id)
    if user is None:
        return page_not_found('')
    all_videos = db_sess.query(Video).all()
    if len(all_videos) > 3:
        last_videos = all_videos[len(all_videos) - 3:][::-1]
    else:
        last_videos = all_videos[::-1]
    title = current_video.title
    author_id = current_video.author
    author = db_sess.query(User).get(author_id)
    like = False
    subscription = False
    if current_user.is_authenticated:
        likes = json.loads(current_user.likes)
        subscriptions = json.loads(current_user.subscriptions)
        if video_id in likes:
            like = True
        if author_id in subscriptions:
            subscription = True
    params = {
        'title': f'{title} - {author.name} {author.surname}',
        'current_video': current_video,
        'video_id': video_id,
        'video_src': url_for("static", filename=f'vid/{video_id}.mp4'),
        'author': author,
        'like': like,
        'subscription': subscription,
        'last_videos': last_videos,
        'db_sess': db_sess,
        'User': User,
        'Video': Video,
        'authenticated': current_user.is_authenticated,
        'current_user': current_user
    }
    return render_template('video.html', **params)


@app.route('/add_video', methods=['GET', 'POST'])
def add_video():
    """
    Возвращает страницу добавления видео если пользователь авторизован,
    иначе доступ запрещен
    """
    if not current_user.is_authenticated:
        return forbidden('')
    form = VideoForm()
    params = {
        'title': 'Добавление видео',
        'authenticated': current_user.is_authenticated,
        'current_user': current_user
    }
    if form.validate_on_submit():
        video_file = request.files['video']
        if not video_file.filename.lower().endswith('.mp4'):
            return render_template('add_video.html',
                                   message='Данный формат видео не поддерживается. '
                                           'Пожалуйста, загрузите видео в формате mp4.',
                                   form=form, **params)
        preview_file = request.files['preview']
        if not preview_file.filename.lower().endswith('.jpg'):
            return render_template('add_video.html',
                                   message='Данный формат обложки не поддерживается. '
                                           'Пожалуйста, загрузите изображение в формате jpg.',
                                   form=form, **params)
        video = Video()
        video.title = form.title.data
        video.description = '<br>'.join(form.description.data.split('\n'))
        video.author = current_user.id
        db_sess.add(video)
        db_sess.commit()
        video_file.save(os.path.join('static/vid', f'{video.id}.mp4'))
        preview_file.save(os.path.join('static/pre', f'{video.id}.jpg'))
        with Image.open(f'static/pre/{video.id}.jpg') as preview_file:
            width, height = preview_file.size
            if width >= height:
                new_width = height * 16 // 9
                delta = (width - new_width) // 2
                preview_file = preview_file.crop((delta, 0, new_width + delta, height))
            else:
                new_height = width * 9 // 16
                delta = (height - new_height) // 2
                preview_file = preview_file.crop((0, delta, width, new_height + delta))
            preview_file.save(f'static/pre/{video.id}.jpg')
        return redirect('/')
    return render_template('add_video.html', form=form, **params)


@app.route('/edit_video/<int:video_id>', methods=['GET', 'POST'])
def edit_video(video_id):
    """
    Возвращает страницу редактирования видео
    если пользователь авторизован и является автором,
    иначе доступ запрщен
    """
    form = VideoForm()
    video = db_sess.query(Video).get(video_id)
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
                                   message='Данный формат видео не поддерживается',
                                   form=form, **params)
        preview_file = request.files['preview']
        if not preview_file.filename.lower().endswith('.jpg'):
            return render_template('edit_video.html',
                                   message='Данный формат обложки не поддерживается',
                                   form=form, **params)
        video.title = form.title.data
        video.description = '<br>'.join(form.description.data.split('\n'))
        db_sess.commit()
        video_file.save(os.path.join('static/vid', f'{video.id}.mp4'))
        preview_file.save(os.path.join('static/pre', f'{video.id}.jpg'))
        with Image.open(f'static/pre/{video.id}.jpg') as preview_file:
            width, height = preview_file.size
            if width >= height:
                new_width = height * 16 // 9
                delta = (width - new_width) // 2
                preview_file = preview_file.crop((delta, 0, new_width + delta, height))
            else:
                new_height = width * 9 // 16
                delta = (height - new_height) // 2
                preview_file = preview_file.crop((0, delta, width, new_height + delta))
            preview_file.save(f'static/pre/{video.id}.jpg')
        return redirect('/')
    return render_template('edit_video.html', form=form, **params)


@app.route('/delete_video/<int:video_id>')
def delete_video(video_id):
    """
    Удаляет видео если пользователь авторизован и является автором,
    иначе доступ запрещен
    """
    video = db_sess.query(Video).get(video_id)
    if current_user.id != video.author:
        return redirect('/')
    db_sess.delete(video)
    db_sess.commit()
    os.remove(os.path.join('static/vid', f'{video.id}.mp4'))
    os.remove(os.path.join('static/pre', f'{video.id}.jpg'))
    return redirect(f'/user/{current_user.id}')


@app.route('/user/<int:user_id>')
def user(user_id):
    """Возвращает страницу выбранного пользователя с его видео"""
    user = db_sess.query(User).get(user_id)
    if user is None:
        return page_not_found('')
    videos = db_sess.query(Video).filter(Video.author == user_id).all()[::-1]
    subscription = False
    if current_user.is_authenticated:
        subscriptions = json.loads(current_user.subscriptions)
        if user_id in subscriptions:
            subscription = True
    params = {
        'title': f'{user.name} {user.surname}',
        'user': user,
        'videos': [videos[i * 3:i * 3 + 3] for i in range(len(videos) // 3)] +
                  [videos[(len(videos) // 3) * 3:]],
        'subscription': subscription,
        'empty': True if len(videos) == 0 else False,
        'authenticated': current_user.is_authenticated,
        'current_user': current_user
    }
    return render_template('user.html', **params)


@app.route('/feed')
def feed():
    """
    Возвращает страницу с лентой видео от людей,
    на которых подписан пользователь.
    Если пользователь не авторизован, доступ запрещен
    """
    if not current_user.is_authenticated:
        return forbidden('')
    subscriptions = json.loads(current_user.subscriptions)
    videos = []
    for i in subscriptions:
        videos += db_sess.query(Video).filter(Video.author == i).all()[::-1][:12]
    new_videos = sorted(videos, key=lambda x: x.datetime)[::-1]
    new_videos = [
        {
            'video': i,
            'author': db_sess.query(User).get(i.author)
        }
        for i in new_videos
    ]
    params = {
        'title': f'Лента',
        'new_videos': [new_videos[i * 3:i * 3 + 3] for i in range(len(new_videos) // 3)] +
                      [new_videos[(len(new_videos) // 3) * 3:]],
        'empty': True if len(new_videos) == 0 else False,
        'subscripted': True if len(subscriptions) != 0 else False,
        'authenticated': current_user.is_authenticated,
        'current_user': current_user
    }
    return render_template('feed.html', **params)


@app.route('/favorite')
def favorite():
    """
    Возвращает страницу с любимыми видео пользователя.
    Если пользователь не авторизован, доступ запрещен
    """
    if not current_user.is_authenticated:
        return forbidden('')
    likes = json.loads(current_user.likes)[::-1]
    liked_videos = [
        {
            'video': db_sess.query(Video).get(i),
            'author': db_sess.query(User).get(db_sess.query(Video).get(i).author)
        }
        for i in likes
    ]
    params = {
        'title': f'Любимое',
        'liked_videos': [liked_videos[i * 3:i * 3 + 3] for i in range(len(liked_videos) // 3)] +
                        [liked_videos[(len(liked_videos) // 3) * 3:]],
        'empty': True if len(liked_videos) == 0 else False,
        'authenticated': current_user.is_authenticated,
        'current_user': current_user
    }
    return render_template('favorite.html', **params)


@app.route('/people')
def people():
    """
    Возвращает страницу с пользователями, на которых подписан пользователь.
    Если пользователь не авторизован, доступ запрещен
    """
    if not current_user.is_authenticated:
        return forbidden('')
    subscriptions = json.loads(current_user.subscriptions)
    subscripted_users = [
        {
            'user': db_sess.query(User).get(i)
        }
        for i in subscriptions
    ]
    subscripted_users.sort(key=lambda x: x['user'].name + x['user'].surname + x['user'].login)
    params = {
        'title': f'Люди',
        'subscripted_users': subscripted_users,
        'empty': True if len(subscripted_users) == 0 else False,
        'authenticated': current_user.is_authenticated,
        'current_user': current_user
    }
    return render_template('people.html', **params)


@app.route('/search')
def search():
    """Возвращает страницу с результатами поиска видео"""
    query = request.args['search']
    videos = db_sess.query(Video).filter(Video.title == query).all()
    params = {
        'title': f'Поиск: {query}',
        'query': query,
        'videos': videos,
        'empty': len(videos) == 0,
        'db_sess': db_sess,
        'User': User,
        'authenticated': current_user.is_authenticated,
        'current_user': current_user
    }
    return render_template('search.html', **params)


db_session.global_init("db/hosting.sql")
db_sess = db_session.create_session()
api.add_resource(UsersResource, '/api/users/<int:user_id>')
api.add_resource(UserListResource, '/api/users')
api.add_resource(VideosResource, '/api/videos/<int:video_id>')
api.add_resource(VideoListResource, '/api/videos')
api.add_resource(LikeResource, '/api/like/<int:video_id>')
api.add_resource(NotLikeResource, '/api/not_like/<int:video_id>')
api.add_resource(FollowResource, '/api/follow/<int:user_id>')
api.add_resource(NotFollowResource, '/api/not_follow/<int:user_id>')

if __name__ == '__main__':
    app.run()
