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
import sys
import yaml

import krejoinstack.plugins.base as base

LOG = log.getLogger("krejoin")


class CustomShells(base.KRJPlugin):
    name = "Custom"

    def __init__(self, plugin_args):
        self.configs = plugin_args
        if self.configs.print_skell:
            self._print_skel()
            exit(0)

        super(CustomShells, self).__init__(plugin_args)

    def _print_skel(self):
        # TODO: Implement this
        pass

    def _load_shells(self):
        if self.configs.template:
            LOG.warning("Parsing template file: %s" % self.configs.template)
            stream = open(self.configs.template, 'r')
            json_template = yaml.load(stream, Loader=yaml.FullLoader)

            sessions = json_template.get('sessions', [])
            if len(sessions) == 0:
                LOG.warning("Malformated template file. 'sessions' not defined")
                sys.exit(1)

            self.sessions = sessions
        else:
            LOG.warning("--template option is needed for the Custom plugin")
            sys.exit(1)

    @staticmethod
    def add_args(parser):
        custom_parameters = parser.add_argument_group(CustomShells.name)
        custom_parameters.add_argument(
            "--custom-template", metavar='<template file path>',
            help='Loads windows and tab based on this template.')
        custom_parameters.add_argument(
            "--print-skell", action='store_true',
            help='Prints a sample template example.')

    @staticmethod
    def help():
        msg = ("This template allows you to especify command sequences to be "
               "run in each window and tab. It reads the layout from a YAML "
               "file. The commands don't need to be mean to run in the local "
               "machine. If you ssh to another host, the next command will be "
               "run in that host.")
        return msg

