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


import konsole
import argparse
from krejoinstack.plugins.juju import JujuSessions
from krejoinstack.plugins.devstack import Devstack
from krejoinstack.plugins.custom import CustomShells

ALL_BACKENDS = [JujuSessions, Devstack, CustomShells]


def main():
    parser = argparse.ArgumentParser(description='Open windowns from a given'
                                                 'environment into Konsole')
    plugin_selector_group = parser.add_mutually_exclusive_group(required=True)
    plugin_selector_group.add_argument("--juju", action='store_true')
    plugin_selector_group.add_argument("--devstack", action='store_true')
    plugin_selector_group.add_argument("--custom", action='store_true')
    parser.add_argument("host", metavar='<user@host>')

    for be in [JujuSessions, Devstack, CustomShells]:
        be.add_args(parser)

    args = parser.parse_args()

    backend = None
    for be in [(args.juju, JujuSessions),
               (args.devstack, Devstack),
               (args.custom, CustomShells)]:
        if be[0]:
            backend_class = be[1]
            backend = backend_class(args)
            break

    if not backend:
        print("Error! No backend found!")
        exit(1)

    backend.spawn()


if __name__ == "__main__":
    main()

    exit(0)
