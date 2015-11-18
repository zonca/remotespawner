"""RemoteSpawner implementation"""
import signal
import errno
import pwd
import os
import pipes
import subprocess
from string import Template

from tornado import gen

from jupyterhub.spawner import Spawner
from IPython.utils.traitlets import (
    Instance, Integer, Unicode
)

from jupyterhub.utils import random_port
from jupyterhub.spawner import set_user_setuid

job_template = {"comet":('''#!/bin/bash
#SBATCH --job-name="SUjupyter"
#SBATCH --output="jupyterhub.%j.%N.out"
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=24
#SBATCH --export=ALL
#SBATCH -t {hours}:00:00

module load python scipy

# create notebooks folder if not already there
mkdir -p ~/notebooks

# create tunnelbot private SSH key
TUNNELBOT_RSA_PATH=(mktemp)
echo "{tunnelbot_rsa}" > $TUNNELBOT_RSA_PATH 
chmod 600 $TUNNELBOT_RSA_PATH

# create tunnel from Comet to Jupyterhub
ssh -o "StrictHostKeyChecking no" -i $TUNNELBOT_RSA_PATH -N -f -R {port}:localhost:{port} tunnelbot@67.58.50.67

    '''), "gordon":    Template('''
#PBS -S /bin/bash
#PBS -l nodes=1:ppn=1,walltime=00:$hours:00,pvmem=${mem}gb
#PBS -N $id
#PBS -q $queue
#####PBS -A usplanck
#PBS -r n
#PBS -o s_$id.log
#PBS -j oe
#PBS -V

module load pycmb

which jupyterhub-singleuser

# setup tunnel for notebook
ssh -N -f -R $port:localhost:$port jupyter.ucsd.edu
# setup tunnel for API
#ssh -N -f -L 8081:localhost:8081 jupyter.ucsd.edu
''')}

class RemoteSpawner(Spawner):
    """A Spawner that just uses Popen to start local processes."""

    KILL_TIMEOUT = Integer(5, config=True, \
        help="Seconds to wait for job to halt after canceling before giving up"
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

        self.log.info("Spawning %s", ' '.join(cmd))
        for k in ["JPY_API_TOKEN"]:
            cmd.insert(0, 'export %s="%s";' % (k, env[k]))
        #self.pid, stdin, stdout, stderr = execute(self.channel, ' '.join(cmd))
        # self.pid = 0
        serialpbs = job_template["comet"]
        queue = "normal"
        mem = 20
        hours = 1
        id = "jup"
        with open(os.environ["TUNNELBOT_RSA_KEY_PATH"]) as rsa_file:
            tunnelbot_rsa = rsa_file.read()

        serialpbs = serialpbs.format(queue = queue, mem = mem, hours=hours, id=id, port=self.user.server.port, PATH="$PATH", tunnelbot_rsa=tunnelbot_rsa)
        serialpbs+='\n'
        serialpbs+='cd %s' % "notebooks"
        serialpbs+='\n'
        serialpbs+=' '.join(cmd)
        print('Submitting *****{\n%s\n}*****' % serialpbs)
        popen = subprocess.Popen('gsissh comet.sdsc.edu sbatch',shell = True, stdin = subprocess.PIPE, stdout = subprocess.PIPE, env=dict(X509_USER_PROXY="/tmp/cert.{}".format(self.user.name)))
        
        out = popen.communicate(serialpbs.encode())[0].strip()

    def get_jobs(self, user):
        jobs = subprocess.check_output(["gsissh", "comet.sdsc.edu", "'squeue -u $USER'"], env=dict(X509_USER_PROXY="/tmp/cert.{}".format(user.name))).decode("utf-8").split("\n")
        self.log.info("squeue results: %s", jobs)
        running_jobs = [j for j in jobs if "SUjupy" in j and ("R" in j or "PD" in j)]
        return running_jobs

    @gen.coroutine
    def poll(self):
        """Check if the single-user process is running

        return None if it is, an exit status (0 if unknown) if it is not.
        """
        jobs = self.get_jobs(self.user)
        if len(jobs) > 1:
            self.log.error("More than one jupyter job")
        elif len(jobs) == 0:
            self.log.info("No jupyterhub job found in running state")
            return 0
        return None

    @gen.coroutine
    def _signal(self, sig):
        """simple implementation of signal

        we can use it when we are using setuid (we are root)"""
        return True # process exists

    @gen.coroutine
    def stop(self, now=False):
        """stop the subprocess

        if `now`, skip waiting for clean shutdown
        """
        # check if process already closed
        status = yield self.poll()
        if status is not None:
            return
        jobs = self.get_jobs(self.user)
        for job in jobs:
            job_number = job.strip().split()[0]
            subprocess.call(["gsissh", "comet.sdsc.edu", "scancel", job_number], env=dict(X509_USER_PROXY="/tmp/cert.{}".format(self.user.name)))
        yield self.wait_for_death(self.KILL_TIMEOUT)

        status = yield self.poll()
        if status is None:
            # it all failed, zombie process
            self.log.warn("Job for user %s never died", self.user.name)

if __name__ == "__main__":

        run_jupyterhub_singleuser("jupyterhub-singleuser", 3434)
