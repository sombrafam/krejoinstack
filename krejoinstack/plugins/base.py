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

import krejoinstack.konsole as konsole


class KRJPlugin(object):
    name = None

    def __init__(self):

        self.konsole = konsole.Konsole()

    @staticmethod
    def new():
        pass

    @staticmethod
    def add_args(parser):
        pass

    def help(self):
        pass

    def launch(self, konsole):
        pass