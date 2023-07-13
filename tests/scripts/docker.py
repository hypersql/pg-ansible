import json
import re
import shlex
import subprocess
import yaml

class DockerInventory():
    def __init__(self, cwd='.'):
        self.cwd = cwd
        self.containers = []

    def discover(self):
        cp = subprocess.run(
            ['docker', 'compose', 'ps', '--format', 'json'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=self.cwd,
        )

        if cp.returncode != 0:
            raise Exception(cp.stderr.decode('utf-8'))

        b_output = cp.stdout
        if len(b_output) > 0:
            self.containers = json.loads(b_output)

class DockerContainer():
    def __init__(self, id):
        self.id = id

    def exec(self, command):
        a_command = shlex.split(command)
        cp = subprocess.run(
            ['docker', 'exec', self.id] + a_command,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        if cp.returncode != 0:
            raise Exception(cp.stderr.decode('utf-8'))
        return cp.stdout

    def send_file(self, local, dest):
        cp = subprocess.run(
            ['docker', 'cp', local, '%s:%s' % (self.id, dest)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        if cp.returncode != 0:
            raise Exception(cp.stderr.decode('utf-8'))

    def ip(self):
        b_output = self.exec('/sbin/ip addr show eth0')
        output = b_output.decode('utf-8')

        m = re.search(r'inet ([0-9\.]+)', output)
        if m:
            return m.group(1)

    def mkdir(self, dir, mode='0700'):
        self.exec('/bin/mkdir -p %s' % dir)
        self.exec('/bin/chmod %s %s' % (mode, dir))

    def rm(self, path):
        self.exec('/bin/rm -rf %s' % path)

    def add_ssh_pub_key(self, ssh_pub_key_path):
        self.send_file(ssh_pub_key_path, '/root/.ssh/authorized_keys')
        self.exec('/bin/chmod 0600 /root/.ssh/authorized_keys')
        self.exec('/bin/chown root:root /root/.ssh/authorized_keys')

    def setup_ssh_server(self):
        self.exec('mkdir -p /run/sshd')
        self.exec('chmod 755 /run/sshd')
        self.exec('ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key')
        self.exec('ssh-keygen -t dsa -f /etc/ssh/ssh_host_dsa_key')
        self.exec('/usr/sbin/sshd')

def DockerOSContainer(id, os):
    with open('../../test-config.yml') as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
        if os not in config['available_os_types']:
            raise Exception("Unknown OS %s" % os)

    return DockerContainer(id)
