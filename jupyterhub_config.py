# Configuration file for jupyterhub.

c = get_config()

#------------------------------------------------------------------------------
# JupyterHub configuration
#------------------------------------------------------------------------------

# An Application for starting a Multi-User Jupyter Notebook server.

# JupyterHub will inherit config from: Application

# The prefix for the hub server. Must not be '/'
# c.JupyterHub.hub_prefix = '/hub/'

# Set the log level by value or name.
import logging
c.JupyterHub.log_level = logging.DEBUG

# The command to start the http proxy.
# 
# Only override if configurable-http-proxy is not on your PATH
# c.JupyterHub.proxy_cmd = 'configurable-http-proxy'

# The base URL of the entire application
# c.JupyterHub.base_url = '/'

# The date format used by logging formatters for %(asctime)s
# c.JupyterHub.log_datefmt = '%Y-%m-%d %H:%M:%S'

# The location of jupyterhub data files (e.g. /usr/local/share/jupyter/hub)
# c.JupyterHub.data_files_path = '/home/zonca/anaconda/envs/jupypy3/share/jupyter/hub'

# Class for authenticating users.
# 
# This should be a class with the following form:
# 
# - constructor takes one kwarg: `config`, the IPython config object.
# 
# - is a tornado.gen.coroutine
# - returns username on success, None on failure
# - takes two arguments: (handler, data),
#   where `handler` is the calling web.RequestHandler,
#   and `data` is the POST form data from the login page.
# c.JupyterHub.authenticator_class = <class 'jupyterhub.auth.PAMAuthenticator'>

# The port for this process
# c.JupyterHub.hub_port = 8081

# The port for the proxy API handlers
# c.JupyterHub.proxy_api_port = 0

# url for the database. e.g. `sqlite:///jupyterhub.sqlite`
# c.JupyterHub.db_url = 'sqlite:///jupyterhub.sqlite'

# Include any kwargs to pass to the database connection. See
# sqlalchemy.create_engine for details.
# c.JupyterHub.db_kwargs = {}

# The public facing ip of the proxy
# c.JupyterHub.ip = ''

# Purge and reset the database.
# c.JupyterHub.reset_db = False

# The Logging format template
# c.JupyterHub.log_format = '[%(name)s]%(highlevel)s %(message)s'

# Supply extra arguments that will be passed to Jinja environment.
# c.JupyterHub.jinja_environment_options = {}

# The cookie secret to use to encrypt cookies.
# 
# Loaded from the JPY_COOKIE_SECRET env variable by default.
# c.JupyterHub.cookie_secret = b''

# Path to SSL key file for the public facing interface of the proxy
# 
# Use with ssl_cert
# c.JupyterHub.ssl_key = ''

# 
# c.JupyterHub.tornado_settings = {}

# Path to SSL certificate file for the public facing interface of the proxy
# 
# Use with ssl_key
# c.JupyterHub.ssl_cert = ''

# Generate default config file
# c.JupyterHub.generate_config = False

# The config file to load
# c.JupyterHub.config_file = 'jupyterhub_config.py'

# log all database transactions. This has A LOT of output
# c.JupyterHub.debug_db = False

# set of usernames of admin users
# 
# If unspecified, only the user that launches the server will be admin.
# c.JupyterHub.admin_users = set()

# The ip for the proxy API handlers
# c.JupyterHub.proxy_api_ip = 'localhost'

# The class to use for spawning single-user servers.
# 
# Should be a subclass of Spawner.
c.JupyterHub.spawner_class = 'remotespawner.RemoteSpawner'

# Interval (in seconds) at which to update last-activity timestamps.
# c.JupyterHub.last_activity_interval = 300

# File to write PID Useful for daemonizing jupyterhub.
# c.JupyterHub.pid_file = ''

# The ip for this process
# c.JupyterHub.hub_ip = 'localhost'

# Interval (in seconds) at which to check if the proxy is running.
# c.JupyterHub.proxy_check_interval = 30

# The public facing port of the proxy
# c.JupyterHub.port = 8000

# The Proxy Auth token.
# 
# Loaded from the CONFIGPROXY_AUTH_TOKEN env variable by default.
# c.JupyterHub.proxy_auth_token = ''

# Answer yes to any questions (e.g. confirm overwrite)
# c.JupyterHub.answer_yes = False

# File in which to store the cookie secret.
# c.JupyterHub.cookie_secret_file = 'jupyterhub_cookie_secret'

#------------------------------------------------------------------------------
# Spawner configuration
#------------------------------------------------------------------------------

# Base class for spawning single-user notebook servers.
# 
# Subclass this, and override the following methods:
# 
# - load_state - get_state - start - stop - poll

# Timeout (in seconds) before giving up on the spawner.
# 
# This is the timeout for start to return, not the timeout for the server to
# respond. Callers of spawner.start will assume that startup has failed if it
# takes longer than this. start should return when the server process is started
# and its location is known.
# c.Spawner.start_timeout = 60

# Whitelist of environment variables for the subprocess to inherit
# c.Spawner.env_keep = ['PATH', 'PYTHONPATH', 'CONDA_ROOT', 'CONDA_DEFAULT_ENV', 'VIRTUAL_ENV', 'LANG', 'LC_ALL']

# Interval (in seconds) on which to poll the spawner.
# c.Spawner.poll_interval = 30

# Enable debug-logging of the single-user server
c.Spawner.debug = True

# The notebook directory for the single-user server
# 
# `~` will be expanded to the user's home directory
# c.Spawner.notebook_dir = ''

# The command used for starting notebooks.
# c.Spawner.cmd = ['jupyterhub-singleuser']

#------------------------------------------------------------------------------
# LocalProcessSpawner configuration
#------------------------------------------------------------------------------

# A Spawner that just uses Popen to start local processes.

# LocalProcessSpawner will inherit config from: Spawner

# Timeout (in seconds) before giving up on the spawner.
# 
# This is the timeout for start to return, not the timeout for the server to
# respond. Callers of spawner.start will assume that startup has failed if it
# takes longer than this. start should return when the server process is started
# and its location is known.
# c.LocalProcessSpawner.start_timeout = 60
c.RemoteSpawner.server_url = "docker3"
c.RemoteSpawner.server_user = "zonca"

# Whitelist of environment variables for the subprocess to inherit
# c.LocalProcessSpawner.env_keep = ['PATH', 'PYTHONPATH', 'CONDA_ROOT', 'CONDA_DEFAULT_ENV', 'VIRTUAL_ENV', 'LANG', 'LC_ALL']

# The notebook directory for the single-user server
# 
# `~` will be expanded to the user's home directory
# c.LocalProcessSpawner.notebook_dir = ''

# Seconds to wait for process to halt after SIGINT before proceeding to SIGTERM
# c.LocalProcessSpawner.INTERRUPT_TIMEOUT = 10

# Seconds to wait for process to halt after SIGKILL before giving up
# c.LocalProcessSpawner.KILL_TIMEOUT = 5

# Enable debug-logging of the single-user server
# c.LocalProcessSpawner.debug = False

# Interval (in seconds) on which to poll the spawner.
# c.LocalProcessSpawner.poll_interval = 30

# Seconds to wait for process to halt after SIGTERM before proceeding to SIGKILL
# c.LocalProcessSpawner.TERM_TIMEOUT = 5

# The command used for starting notebooks.
# c.LocalProcessSpawner.cmd = ['jupyterhub-singleuser']

#------------------------------------------------------------------------------
# Authenticator configuration
#------------------------------------------------------------------------------

# A class for authentication.
# 
# The API is one method, `authenticate`, a tornado gen.coroutine.

# Username whitelist.
# 
# Use this to restrict which users can login. If empty, allow any user to
# attempt login.
# c.Authenticator.whitelist = set()

#------------------------------------------------------------------------------
# PAMAuthenticator configuration
#------------------------------------------------------------------------------

# Authenticate local *ix users with PAM

# PAMAuthenticator will inherit config from: LocalAuthenticator, Authenticator

# If a user is added that doesn't exist on the system, should I try to create
# the system user?
# c.PAMAuthenticator.create_system_users = False

# The encoding to use for PAM
# c.PAMAuthenticator.encoding = 'utf8'

# The PAM service to use for authentication.
# c.PAMAuthenticator.service = 'login'

# Username whitelist.
# 
# Use this to restrict which users can login. If empty, allow any user to
# attempt login.
# c.PAMAuthenticator.whitelist = set()
