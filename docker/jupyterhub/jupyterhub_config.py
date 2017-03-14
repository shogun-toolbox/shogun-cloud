# jupyterhub_config.py
c = get_config()

import os
pjoin = os.path.join

runtime_dir = '/srv/jupyterhub'
if not os.path.exists(runtime_dir):
    os.makedirs(runtime_dir)

if 'SSL_KEY' in os.environ and 'SSL_CERT' in os.environ:
    c.JupyterHub.ssl_key = os.environ['SSL_KEY']
    c.JupyterHub.ssl_cert = os.environ['SSL_CERT']

c.JupyterHub.hub_ip = '0.0.0.0'

c.JupyterHub.spawner_class = 'marathonspawner.MarathonSpawner'
c.MarathonSpawner.app_image = os.environ.get('NB_DOCKER_IMAGE')
c.MarathonSpawner.app_prefix = os.environ.get('MARATHON_APP_GROUP')
c.MarathonSpawner.marathon_host = os.environ.get('MARATHON_MASTER')
c.MarathonSpawner.marathon_constraints = os.getenv('MARATHON_CONSTRAINTS', [])
c.MarathonSpawner.notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/jovyan/work'
c.MarathonSpawner.hub_ip_connect = os.environ.get('JUPYTERHUB_IP_CONNECT')
c.MarathonSpawner.hub_port_connect = int(os.environ.get('JUPYTERHUB_PORT_CONNECT'))
c.MarathonSpawner.mem_limit = os.getenv('NOTEBOOK_MEMORY_LIMIT', '2G')
c.MarathonSpawner.cpu_limit = float(os.getenv('NOTEBOOK_CPU_LIMIT', 2.0))
c.MarathonSpawner.start_timeout = int(os.getenv('JUPYTERHUB_START_TIMEOUT', '60'))
c.MarathonSpawner.http_timeout = int(os.getenv('JUPYTERHUB_HTTP_TIMEOUT', '60'))
c.MarathonSpawner.poll_interval = int(os.getenv('JUPYTERHUB_POLL_INTERVAL', '30'))


def volumes(env_var):
    if env_var in os.environ:
        import json
        return json.loads(os.environ[env_var])
    return []

c.MarathonSpawner.volumes = volumes('NB_DOCKER_VOLUMES')

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
    import re
    parts = re.split("\s*,\s*", os.environ[varname])
    return set([part for part in parts if len(part) > 0])

# specify admin
c.Authenticator.admin_users = userlist("JUPYTERHUB_ADMINS")
c.JupyterHub.admin_access = True
