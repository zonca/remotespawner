"""RemoteSpawner implementation"""
import signal
import errno
import pwd
import os
import pipes
from subprocess import Popen, call
import subprocess
from string import Template

from tornado import gen

from jupyterhub.spawner import Spawner
from IPython.utils.traitlets import (
    Instance, Integer, Unicode
)

from jupyterhub.utils import random_port
from jupyterhub.spawner import set_user_setuid

import paramiko

def setup_ssh_tunnel(port, user, server):
    """Setup a local SSH port forwarding"""
    #tunnel.openssh_tunnel(port, port, "%s@%s" % (user, server))
    call(["ssh", "-N", "-f", "%s@%s" % (user, server),
          "-L {port}:localhost:{port}".format(port=port)])

def run_jupyterhub_singleuser(cmd, port, name):
# GORDON
#     serialpbs = Template('''
# #PBS -S /bin/bash
# #PBS -l nodes=1:ppn=1,walltime=00:$hours:00,pvmem=${mem}gb
# #PBS -N $id
# #PBS -q $queue
# #####PBS -A usplanck
# #PBS -r n
# #PBS -o s_$id.log
# #PBS -j oe
# #PBS -V
# 
# module load pycmb
# 
# which jupyterhub-singleuser
# 
# # setup tunnel for notebook
# ssh -N -f -R $port:localhost:$port jupyter.ucsd.edu
# # setup tunnel for API
# #ssh -N -f -L 8081:localhost:8081 jupyter.ucsd.edu
# 
#     ''')
# COMET
    serialpbs = Template('''#!/bin/bash
#SBATCH --job-name="jupyterhub"
#SBATCH --output="jupyterhub.%j.%N.out"
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=24
#SBATCH --export=ALL
#SBATCH -t 00:$hours:00

which jupyterhub-singleuser

# setup tunnel for notebook
ssh -N -f -R $port:localhost:$port jupyter.calit2.optiputer.net
# setup tunnel for API
# ssh -N -f -L 9081:localhost:9081 jupyter.calit2.optiputer.net

    ''')
    queue = "usplanck"
    queue = "normal"
    mem = 20
    hours = 10
    id = "jup"
    serialpbs = serialpbs.substitute(dict(queue = queue, mem = mem, hours=hours, id=id, port=port, PATH="$PATH"))
    serialpbs+='\n'
    serialpbs+='cd %s' % "notebooks"
    serialpbs+='\n'
    serialpbs+=cmd
    print('Submitting *****{\n%s\n}*****' % serialpbs)
    # popen = subprocess.Popen('ssh carver.nersc.gov /usr/syscom/opt/torque/default_sl5carver/bin/qsub',shell = True, stdin = subprocess.PIPE, stdout = subprocess.PIPE)
    # popen = subprocess.Popen('gsissh comet.sdsc.edu sbatch',shell = True, stdin = subprocess.PIPE, stdout = subprocess.PIPE)
    popen = subprocess.Popen('ssh comet.sdsc.edu sbatch',shell = True, stdin = subprocess.PIPE, stdout = subprocess.PIPE,
    preexec_fn=set_user_setuid(name)
    )
    out = popen.communicate(serialpbs.encode())[0].strip()
    return out

# def execute(channel, command):
#     """Execute command and get remote PID"""
# 
#     command = command + '& pid=$!; echo PID=$pid'
#     stdin, stdout, stderr = channel.exec_command(command)
#     pid = int(stdout.readline().replace("PID=", ""))
#     return pid, stdin, stdout, stderr

class RemoteSpawner(Spawner):
    """A Spawner that just uses Popen to start local processes."""

    INTERRUPT_TIMEOUT = Integer(1200, config=True, \
        help="Seconds to wait for process to halt after SIGINT before proceeding to SIGTERM"
                               )
    TERM_TIMEOUT = Integer(1200, config=True, \
        help="Seconds to wait for process to halt after SIGTERM before proceeding to SIGKILL"
                          )
    KILL_TIMEOUT = Integer(1200, config=True, \
        help="Seconds to wait for process to halt after SIGKILL before giving up"
                          )

    server_url = Unicode("localhost", config=True, \
        help="url of the remote server")
    server_user = Unicode("jupyterhub", config=True, \
        help="user with passwordless SSH access to the server")

    # channel = Instance(paramiko.client.SSHClient)
    pid = Integer(0)

    def make_preexec_fn(self, name):
        """make preexec fn"""
        return set_user_setuid(name)

    def load_state(self, state):
        """load pid from state"""
        super(RemoteSpawner, self).load_state(state)
        # if 'pid' in state:
        #     self.pid = state['pid']

    def get_state(self):
        """add pid to state"""
        state = super(RemoteSpawner, self).get_state()
        # if self.pid:
        #     state['pid'] = self.pid
        return state

    def clear_state(self):
        """clear pid state"""
        #super(RemoteSpawner, self).clear_state()
        #self.pid = 0

    def user_env(self, env):
        """get user environment"""
        env['USER'] = self.user.name
        env['HOME'] = pwd.getpwnam(self.user.name).pw_dir
        return env

    def _env_default(self):
        env = super()._env_default()
        return self.user_env(env)

    @gen.coroutine
    def start(self):
        """Start the process"""
        self.user.server.port = random_port()
        cmd = []
        env = self.env.copy()

        cmd.extend(self.cmd)
        cmd.extend(self.get_args())

        self.log.debug("Env: %s", str(env))
        # self.channel = paramiko.SSHClient()
        # self.channel.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #self.channel.connect(self.server_url, username=self.server_user)
        #self.proc = Popen(cmd, env=env, \
        #    preexec_fn=self.make_preexec_fn(self.user.name),
        #                 )
        self.log.info("Spawning %s", ' '.join(cmd))
        for k in ["JPY_API_TOKEN"]:
            cmd.insert(0, 'export %s="%s";' % (k, env[k]))
        #self.pid, stdin, stdout, stderr = execute(self.channel, ' '.join(cmd))
        # self.pid = 0
        run_jupyterhub_singleuser(' '.join(cmd), name=self.user.name, port=self.user.server.port)
        # self.log.info("Process PID is %i", self.pid)
        #self.user.server.ip = USE A COROUTINE TO GET IT WHEN JOB STARTS
        #self.log.info("Setting up SSH tunnel")
        #setup_ssh_tunnel(self.user.server.port, self.server_user, self.server_url)
        #self.log.debug("Error %s", ''.join(stderr.readlines()))

    @gen.coroutine
    def poll(self):
        """Poll the process"""
        # for now just assume it is ok
        return None
        ### if we started the process, poll with Popen
        ##if self.proc is not None:
        ##    status = self.proc.poll()
        ##    if status is not None:
        ##        # clear state if the process is done
        ##        self.clear_state()
        ##    return status

        ### if we resumed from stored state,
        ### we don't have the Popen handle anymore, so rely on self.pid

        ##if not self.pid:
        ##    # no pid, not running
        ##    self.clear_state()
        ##    return 0

        ### send signal 0 to check if PID exists
        ### this doesn't work on Windows, but that's okay because we don't support Windows.
        ##alive = yield self._signal(0)
        ##if not alive:
        ##    self.clear_state()
        ##    return 0
        ##else:
        ##    return None

    @gen.coroutine
    def _signal(self, sig):
        """simple implementation of signal

        we can use it when we are using setuid (we are root)"""
        #try:
        #    os.kill(self.pid, sig)
        #except OSError as e:
        #    if e.errno == errno.ESRCH:
        #        return False # process is gone
        #    else:
        #        raise
        return True # process exists

    @gen.coroutine
    def stop(self, now=False):
        """stop the subprocess

        if `now`, skip waiting for clean shutdown
        """
        return
        #if not now:
        #    status = yield self.poll()
        #    if status is not None:
        #        return
        #    self.log.debug("Interrupting %i", self.pid)
        #    yield self._signal(signal.SIGINT)
        #    yield self.wait_for_death(self.INTERRUPT_TIMEOUT)

        ## clean shutdown failed, use TERM
        #status = yield self.poll()
        #if status is not None:
        #    return
        #self.log.debug("Terminating %i", self.pid)
        #yield self._signal(signal.SIGTERM)
        #yield self.wait_for_death(self.TERM_TIMEOUT)

        ## TERM failed, use KILL
        #status = yield self.poll()
        #if status is not None:
        #    return
        #self.log.debug("Killing %i", self.pid)
        #yield self._signal(signal.SIGKILL)
        #yield self.wait_for_death(self.KILL_TIMEOUT)

        #status = yield self.poll()
        #if status is None:
        #    # it all failed, zombie process
        #    self.log.warn("Process %i never died", self.pid)

if __name__ == "__main__":

        run_jupyterhub_singleuser("jupyterhub-singleuser", 3434)
