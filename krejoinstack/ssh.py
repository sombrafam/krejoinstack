import exceptions
import logging
import os
import paramiko
import six

from oslo_concurrency import processutils

DEFAULT_PKFILE = os.path.expanduser('~/.ssh/id_rsa')
DEFAULT_KHFILE = os.path.expanduser('~/.ssh/known_hosts')

LOG = logging.getLogger(__name__)


class SSHClient(object):
    def __init__(self, hostip, user='ubuntu', pwd="",
                 pkfile=DEFAULT_PKFILE, khfile=DEFAULT_KHFILE):
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.load_host_keys(khfile)

            try:
                privatekey = paramiko.RSAKey.from_private_key_file(pkfile)
            except exceptions.IOError:
                LOG.error('No private key found in: %s!! Please generate one with'
                          'ssh-keygen.', pkfile)
                exit(1)

            self.ssh.connect(hostip, username=user, password=pwd,
                             pkey=privatekey)
        except paramiko.SSHException as e:
            LOG.error("Can't connect to host %s. Please check if you have "
                      "properly exported your public keys.", hostip)
            LOG.error("%s", six.text_type(e.message))
            exit(1)

    def run(self, cmd, check_exit_status=True):

        stdin_stream, stdout_stream, stderr_stream = self.ssh.exec_command(cmd)
        stdout = stdout_stream.read()
        stderr = stderr_stream.read()
        channel = stdout_stream.channel
        stdin_stream.close()

        exit_status = channel.recv_exit_status()
        if check_exit_status and exit_status != -1 and exit_status != 0:
            raise processutils.ProcessExecutionError(exit_code=exit_status,
                                                     stdout=stdout,
                                                     stderr=stderr,
                                                     cmd=cmd)

        return stdout, stderr
