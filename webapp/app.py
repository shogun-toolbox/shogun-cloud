#!/usr/bin/env python
# coding=utf8

from docker_server import DockerServer, ContainerException
from models import User, db
from flask import Flask, render_template, session, g, redirect
from flask import url_for, request, jsonify
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form, TextField
from flask.ext.login import LoginManager, login_required, current_user, \
    logout_user, login_user
from flask_oauthlib.client import OAuth
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

app = Flask(__name__)
app.config.from_pyfile('app.cfg')
app.config.from_envvar('FLASKAPP_SETTINGS', silent=True)

db.init_app(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

login_manager = LoginManager()
login_manager.init_app(app)

oauth = OAuth(app)
github = oauth.remote_app(
    'github',
    consumer_key=app.config['GITHUB_CONSUMER_KEY'],
    consumer_secret=app.config['GITHUB_CONSUMER_SECRET'],
    request_token_params={'scope': 'user:email'},
    authorize_url='https://github.com/login/oauth/authorize',
    access_token_url='https://github.com/login/oauth/access_token',
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST')

google = oauth.remote_app(
    'google',
    consumer_key=app.config['GOOGLE_CONSUMER_KEY'],
    consumer_secret=app.config['GOOGLE_CONSUMER_SECRET'],
    request_token_params={
        'scope': 'https://www.googleapis.com/auth/userinfo.email \
                  https://www.googleapis.com/auth/userinfo.profile'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth')


docker_client = DockerServer(app.config['DOCKER_SERVERS'][0],
                             app.config['DOCKER_CONTAINER_REPOSITORY'])

Bootstrap(app)


@app.route('/', methods=['GET'])
def index():
    try:
        container = None
        if current_user.is_authenticated():
            container = docker_client.get_or_make_container(current_user)

        return render_template('index.html', container=container,
                               servicehost=app.config['SERVICES_HOST'])
    except ContainerException as e:
        return render_template('error.html', error=e)


def populate_user(username, email):
    user = db.session.query(User) \
		    .filter(User.email == email) \
		    .first()
    if user is None:
        user = User(username, email)
        db.session.add(user)
        db.session.commit()
    return user


@app.route('/github-authorized')
@github.authorized_handler
def github_authorized(resp):
    if resp is None:
            return 'Access denied: reason=%s error=%s' % (
                request.args['error_reason'],
                request.args['error_description']
            )
    session['github_token'] = (resp['access_token'], '')
    userinfo = github.get('user')
    email = userinfo.data['email']
    if email is None:
        email = 'github@%s' % userinfo.data['login']
    user = populate_user(userinfo.data['name'], email)
    login_user(user)

    return redirect(url_for('index'))


@app.route('/google-authorized')
@google.authorized_handler
def google_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )

    session['google_token'] = (resp['access_token'], '')
    userinfo = google.get('userinfo')
    user = populate_user(userinfo.data['name'], userinfo.data['email'])
    login_user(user)

    return redirect(url_for('index'))


@app.route('/login/github')
def login_github():
    return github.authorize(callback=url_for('github_authorized',
                            _external=True))


@app.route('/login/google')
def login_google():
    return google.authorize(callback=url_for('google_authorized',
                            _external=True))


@app.route('/notebook/<name>')
@login_required
def open_notebook(name):
    ipy_port = docker_client.get_container_public_port(current_user.container_id, u'8888')
    print ipy_port
    ipy_url = "http://{}:{}/{}".format(app.config['SERVICES_HOST'],
                                       ipy_port, name)
    return redirect(ipy_url)


@app.route('/seconds-available')
@login_required
def seconds_available():
    avail_seconds = int(app.config['DOCKER_CONTAINER_TIMEOUT'])-docker_client.get_container_uptime(current_user.container_id)
    return jsonify(available_seconds=avail_seconds)


@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')


@github.tokengetter
def get_github_oauth_token():
    return session.get('github_token')


@login_manager.user_loader
def load_user(id):
    return db.session.query(User).get(id) 


@login_manager.unauthorized_handler
def unauthorized():
    return render_template('index.html', activeLogin=True)


@app.route('/logout')
def logout():
    #stop docker container in order to not to waste memory
    docker_client.stop_container(current_user.container_id)

    logout_user()
    return redirect(url_for('index'))


if '__main__' == __name__:
    manager.run()
