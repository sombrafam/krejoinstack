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

import argparse
import logging as log
from krejoinstack.plugins.juju import JujuSessions
from krejoinstack.plugins.devstack import Devstack
from krejoinstack.plugins.custom import CustomShells

LOG = log.getLogger("krejoin")
formatter = log.Formatter('%(levelname)s: %(message)s')

c_handler = log.StreamHandler()
c_handler.setLevel(log.INFO)
c_handler.setFormatter(formatter)
LOG.addHandler(c_handler)

f_handler = log.FileHandler('/tmp/krejoinstack.log')
f_handler.setLevel(log.DEBUG)
f_handler.setFormatter(formatter)
LOG.addHandler(f_handler)

# Always start in debug mode so we can debug what happens before we read
# the --debug option.
LOG.setLevel(log.DEBUG)

ALL_BACKENDS = [JujuSessions, Devstack, CustomShells]


def main():
    parser = argparse.ArgumentParser(
        description='Open windows from a given environment into Konsole tabs.',
        formatter_class=argparse.RawTextHelpFormatter
    )
    plugin_selector_group = parser.add_mutually_exclusive_group(required=True)
    plugin_selector_group.add_argument("--juju", action='store_true')
    plugin_selector_group.add_argument("--devstack", action='store_true')
    plugin_selector_group.add_argument("--custom", action='store_true',
                                       help=CustomShells.help())
    parser.add_argument("--debug", action="store_true", required=False,
                        help="Enables debugging to STDOUT")
    parser.add_argument("host", metavar='<user@host>')

    for be in [JujuSessions, Devstack, CustomShells]:
        be.add_args(parser)

    args = parser.parse_args()
    if args.debug:
        c_handler.setLevel(log.DEBUG)
    else:
        # Disables debug if the user didn't not call --debug as it was set to
        # DEBUG previously
        LOG.setLevel(log.INFO)

    print("%s" % str(args))
    print("args.juju: %s" % str(args.juju))
    print("args.devstack: %s" % str(args.devstack))
    print("args.custom: %s" % str(args.custom))

    backend = None
    for be_is_enabled, backend_class in [(args.juju, JujuSessions),
                                         (args.devstack, Devstack),
                                         (args.custom, CustomShells)]:
        if be_is_enabled:
            backend = backend_class(args)
            break

    if not backend:
        print("Error! No backend found!")
        exit(1)

    backend.spawn()


if __name__ == "__main__":
    main()

    exit(0)
