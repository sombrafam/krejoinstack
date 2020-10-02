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

from abc import ABC, abstractmethod
import logging as log

import krejoinstack.konsole as konsole

LOG = log.getLogger("krejoin")


class NotImplementedError(Exception):
    pass


class KRJPlugin(ABC):
    name = None

    def __init__(self, plugin_args):
        self.konsole = konsole.Konsole('')
        self.sessions = []
        self.configs = plugin_args

    def _load_shells(self):
        raise NotImplementedError

    def spawn(self):
        self._load_shells()
        for window in self.sessions:
            LOG.warning("Looping over windows: %s", window)
            k = self.konsole
            for tab_name, commands in window['tabs'].items():
                LOG.warning("Looping over tabs: %s", tab_name)
                k.new_tab(tab_name)
                for cmd in commands:
                    LOG.warning("Looping over commands: %s", cmd)
                    k.run(tab_name, cmd)


    @staticmethod
    @abstractmethod
    def add_args(parser):
        pass
