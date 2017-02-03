#!/usr/bin/python

import getopt
import konsole
import logging
import os
import six
import ssh
import sys
import time
import socket

from oslo_concurrency import processutils

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

username = 'ubuntu'
host = ''
devstack_dir = ''
DEVSTACK_PATH = '$HOME/devstack'


def print_help():
    print "Usage: %s [options] <host_ip>"
    print "Options:"
    print "    -h: Print this menu and exit."
    print "    -u, --user: Username of the stack host. Default is: ubuntu"
    print ("    -d, --devstack-dir: Directory where devstack is.: Default is: "
           "~/<username>/devstack")


def parse_opt(argv):
    global username, host, devstack_dir

    if len(argv) < 2:
        print_help()
        exit(1)

    try:
        opts, args = getopt.getopt(argv[1:],
                                   'hu:d:',
                                   ['user=', 'devstack-dir=', 'help', 'debug'])
    except getopt.GetoptError as e:
        LOG.debug("Parsing args: %s", six.text_type(e.message))
        print_help()
        sys.exit(1)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print_help()
            sys.exit(0)
        elif opt in ('-u', '--user'):
            username = six.text_type(arg)
        elif opt in ('-d', '--devstack-dir'):
            if os.path.isabs(arg):
                devstack_dir = six.text_type(arg)
            else:
                devstack_dir = os.path.expanduser("$HOME/%s" % arg)
        elif opt is '--debug':
            LOG.setLevel(logging.DEBUG)

    host = args.pop()


def main(argv):
    parse_opt(argv)

    try:
        socket.inet_aton(socket.gethostbyname(host))
        # We are good to proceed
        stack_host = host
    except socket.error:
        LOG.error("The parameter \'%s\' must be a valid IP address or "
                  "hostname", argv[1])
        print_help()
        exit(1)

    client = ssh.SSHClient(stack_host, user=username)

    try:
        devstack_path = devstack_dir or DEVSTACK_PATH
        out, err = client.run("cat %s/stack-screenrc" % devstack_path)
        shells_file_list = out.split('screen')[2:]
    except processutils.ProcessExecutionError:
        LOG.error("Devstack is not installed in %s on the target host.",
                  devstack_path)
        exit(1)

    out, err = client.run('screen -ls stack', check_exit_status=False)
    if 'is a screen on' in out:
        remote_screen_id = out.split('\t')[1]
        LOG.debug("Deleting remote session %s", remote_screen_id)
        client.run('screen -X -S %s quit' % remote_screen_id)
        # TODO(erlon): do this in a cleaner way deleting only the processes
        # related to screen
        client.run('killall -9 /usr/bin/python', check_exit_status=False)

    shells_cmds = []
    for shell in shells_file_list:
        # TODO(erlon): use regular expressions to get these fields
        title = shell.split('\n')[0].split(' ')[2]
        cmd = shell.split('\n')[1].split('\n')[0].split('"')[1].replace('\r', '')
        shells_cmds.append((title, cmd))

    k = konsole.Konsole()
    count = 0
    for sh_title, sh_cmd in shells_cmds:
        if count == 0:
            # the first shell is always created automatically
            shell = k.shells[1]
            shell.rename(sh_title)
            count += 1
        else:
            shell = konsole.KonsoleShell(parent_id=k.pid, name=sh_title)
            k.shells[count] = shell
            count += 1

        shell.ssh_connect(stack_host)
        shell.run(sh_cmd)
        time.sleep(0.2)

    LOG.info('Finish k-rejoingstack suscessfully!')
    exit(0)
