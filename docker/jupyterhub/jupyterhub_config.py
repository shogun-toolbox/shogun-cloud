# jupyterhub_config.py
c = get_config()

import os
pjoin = os.path.join

runtime_dir = '/srv/jupyterhub'
if not os.path.exists(runtime_dir):
    os.makedirs(runtime_dir)

c.JupyterHub.ssl_key = os.environ['SSL_KEY']
c.JupyterHub.ssl_cert = os.environ['SSL_CERT']

c.JupyterHub.hub_ip = '0.0.0.0'

c.JupyterHub.spawner_class = 'marathonspawner.MarathonSpawner'
c.MarathonSpawner.app_image = os.environ.get('NB_DOCKER_IMAGE')
c.MarathonSpawner.app_prefix = os.environ.get('MARATHON_APP_GROUP')
c.MarathonSpawner.marathon_host = os.environ.get('MARATHON_MASTER')
c.MarathonSpawner.marathon_constraints = os.environ.get('MARATHON_CONSTRAINTS')
c.MarathonSpawner.notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/jovyan/work'
c.MarathonSpawner.hub_ip_connect = os.environ.get('HUB_IP_CONNECT')
c.MarathonSpawner.hub_port_connect = os.environ.get('HUB_PORT_CONNECT')

c.MarathonSpawner.volumes = os.environ.get('NB_DOCKER_VOLUMES')

c.JupyterHub.cookie_secret_file = pjoin(runtime_dir, 'cookie_secret')
c.JupyterHub.db_url = pjoin(runtime_dir, 'jupyterhub.sqlite')

# put the log file in /var/log
c.JupyterHub.extra_log_file = pjoin(runtime_dir, 'jupyterhub.log')

# use GitHub OAuthenticator for local users
c.JupyterHub.authenticator_class = 'oauthenticator.GitHubOAuthenticator'
c.GitHubOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']
c.GitHubOAuthenticator.client_id = os.environ['GITHUB_CLIENT_ID']
c.GitHubOAuthenticator.client_secret = os.environ['GITHUB_CLIENT_SECRET']


def userlist(varname):
    """
    Intercept an environment variable as a whitespace-separated list of GitHub
    usernames.
    """
    parts = re.split("\s*,\s*", os.environ[varname])
    return set([part for part in parts if len(part) > 0])

# specify admin
c.Authenticator.admin_users = userlist("JUPYTERHUB_ADMINS")
c.JupyterHub.admin_access = True