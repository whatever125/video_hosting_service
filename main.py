import os
from flask import Flask, render_template, url_for, redirect, request
from data.videos import Video
from data.users import User
from data import db_session
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from data.login_form import LoginForm
from data.register_form import RegisterForm
from data.video_form import VideoForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


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
        'authenticated': current_user.is_authenticated
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
        'authenticated': current_user.is_authenticated
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
        'authenticated': current_user.is_authenticated
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
@login_required
def logout():
    logout_user()
    return redirect("/")


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
        'authenticated': current_user.is_authenticated
    }
    return render_template('video.html', **params)


@app.route('/add_video', methods=['GET', 'POST'])
def add_video():
    form = VideoForm()
    params = {
        'title': 'Загрузка видео',
        'authenticated': current_user.is_authenticated
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
    if current_user.id != video.author:
        return redirect('/')
    params = {
        'title': 'Редактирование видео',
        'video': video,
        'description': '\n'.join(video.description.split('<br>')),
        'authenticated': current_user.is_authenticated
    }
    if form.validate_on_submit():
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
    videos = db_sess.query(Video).filter(Video.author == user_id).all()
    params = {
        'title': f'{user.name} {user.surname}',
        'user': user,
        'videos': videos,
        'authenticated': current_user.is_authenticated
    }
    return render_template('user.html', **params)


def main():
    app.run()


if __name__ == '__main__':
    db_session.global_init("db/hosting.sql")
    db_sess = db_session.create_session()
    main()
