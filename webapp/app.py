#!/usr/bin/env python
# coding=utf8

from docker_server import DockerServer, ContainerException

from flask import Flask, render_template, session, g, redirect
from flask import url_for, request, jsonify
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form, TextField
from flask.ext.login import LoginManager, login_required, current_user, \
    logout_user, login_user
from flask_oauthlib.client import OAuth

app = Flask(__name__)
app.config.from_pyfile('app.cfg')
app.config.from_envvar('FLASKAPP_SETTINGS', silent=True)

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


@app.before_request
def get_current_user():
    if current_user.is_authenticated():
        ipy_port = session.get('ipy_port')
        if ipy_port is not None:
            g.ipy_port = ipy_port


@app.route('/', methods=['GET'])
def index():
    try:
        container = None
        if current_user.is_authenticated():
            container = docker.get_or_make_container(current_user)

        return render_template('index.html', container=container,
                               servicehost=app.config['SERVICES_HOST'])
    except ContainerException as e:
        return render_template('error.html', error=e)


    """
    try:
        container = None
        if current_user.is_authenticated():
            container = get_or_make_container(g.user)
            session['ipy_port'] = container['portmap'][8888]
            if session.get('after_login', ''):
                return redirect(session.get('after_login', ''))
    """


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
    print userinfo
    #User(userinfo['name'], userinfo['email'])
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

    user = User(userinfo['name'], userinfo['email'])
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
    ipy_url = "http://{}:{}/{}".format(app.config['SERVICES_HOST'],
                                       g.ipy_port, name)
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
    return User.query.get(int(id))


@login_manager.unauthorized_handler
def unauthorized():
    return render_template('index.html', activeLogin=True)


@app.route('/logout')
def logout():
    #stop docker container in order to not to waste memory
    docker_client.stop_container(current_user.container_id)

    session.pop('ipy_port', None)
    logout_user()
    return redirect(url_for('index'))


if '__main__' == __name__:
    app.run(debug=True, host='0.0.0.0', port=5001)
