# remotespawner
Remote Spawner class for JupyterHub to spawn IPython notebooks and a remote server and tunnel the port via SSH

Need to have passwordless SSH access to remote server, need to setup `jupyterhub_config.py`:

c.RemoteSpawner.server_url = "docker3" # or IP
c.RemoteSpawner.server_user = "zonca"

And needs the 8081 port of the local machine that runs `jupyterhub` to be forwarded to 
the remote server.

Currently in development, it sort of works.
