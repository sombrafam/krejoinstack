# Copyright (c) 2019 Erlon R. Cruz
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging as log
import time
import six
import subprocess
from distutils import version

LOG = log.getLogger("krejoin")
NEW_KONSOLE_API_VERSION = version.LooseVersion('15.0.0')


class KonsoleSession(object):
    cmd_output = subprocess.check_output(('konsole', '--version'))
    version = version.LooseVersion(cmd_output.decode('utf-8').split()[1])

    set_title_cmd = "qdbus org.kde.konsole-%(kid)s /Sessions/%(sid)s setTitle 1"
    exec_cmd = "qdbus org.kde.konsole-%(kid)s /Sessions/%(sid)s runCommand"

    if version < NEW_KONSOLE_API_VERSION:
        new_session_cmd = "qdbus org.kde.konsole-%(kid)s /Konsole newSession"
    else:
        new_session_cmd = "qdbus org.kde.konsole-%(kid)s /Windows/1 newSession"

    def __init__(self, parent_id, create=True, name=None):
        self.name = name
        self.parent_id = parent_id

        LOG.debug("Konsole version: %s", six.text_type(KonsoleSession.version))

        # the first session is created automatically
        if not create:
            self.sid = 1
            return

        cmd = KonsoleSession.new_session_cmd % {'kid': self.parent_id}
        cmd = cmd.split()
        LOG.debug("cmd: %s", cmd)

        retries = 5
        while retries > 0:
            try:
                out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
                break
            except subprocess.CalledProcessError:
                LOG.debug("Process not yet ready. Waiting 0.5 sec")
                time.sleep(0.5)
                retries -= 1

        self.sid = int(out)
        self._rename(name)

    def _rename(self, name):
        cmd = KonsoleSession.set_title_cmd % {'kid': self.parent_id, 'sid': self.sid}
        cmd = cmd.split()
        cmd.append(name)
        subprocess.call(cmd)

    def run(self, shell_cmd):
        cmd = KonsoleSession.exec_cmd % {'kid': self.parent_id, 'sid': self.sid}
        cmd = cmd.split()
        cmd.append(shell_cmd)
        LOG.debug("Runing command: %s" ' '.join(cmd))
        out = subprocess.call(cmd)
        time.sleep(0.5)

    def ssh_connect(self, host, user='ubuntu'):
        ssh_login = "ssh %(user)s@%(ip)s" % {'user': user, 'ip': host}
        self.run(ssh_login)


class Konsole(object):
    def __init__(self, first_shell_name):
        self.pid = 0
        self.shells = {}

        # creates a new console
        try:
            proc = subprocess.Popen(('konsole', '--nofork'))
        except OSError:
            LOG.error('KDE konsole is not installed!')
            exit(1)

        self.pid = proc.pid

        LOG.debug("Created console %s", six.text_type(self.pid))
        self.shells[first_shell_name] = KonsoleSession(parent_id=self.pid,
                                                       create=False,
                                                       name=first_shell_name)

    def new_tab(self, title):
        sh = KonsoleSession(parent_id=self.pid, name=title)
        self.shells[title] = sh

    def run(self, shell_name, cmd):
        self.shells[shell_name].run(cmd)

