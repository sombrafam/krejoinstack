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

import json
import logging as log
import os
import sys
import yaml

import krejoinstack.plugins.base as base

LOG = log.getLogger("krejoin")


class CustomShells(base.KRJPlugin):
    name = "Custom"

    def __init__(self, plugin_args):
        self.configs = plugin_args
        super(CustomShells, self).__init__(plugin_args)

    @staticmethod
    def print_skel():
        abs_path = os.path.abspath(__file__)
        parent_path = "/".join(abs_path.split('/')[:-2])
        file_path = parent_path + "/resources/common-skel.yaml"
        try:
            stream = open(file_path, 'r')
        except FileNotFoundError:
            LOG.debug("abs_path: %s", abs_path)
            LOG.debug("cwd: %s", os.path.abspath(os.getcwd()))
            LOG.error("Can't find template file %s", file_path)
            sys.exit(1)
        return stream.read()

    def _load_shells(self):
        if not self.configs.custom_template:
            LOG.error("--template option is needed for the Custom plugin")
            sys.exit(1)

        LOG.debug("Parsing template file: %s",
                    self.configs.custom_template)
        try:
            stream = open(self.configs.custom_template, 'r')
        except FileNotFoundError:
            LOG.error("Can't find template file %s",
                      self.configs.custom_template)
            sys.exit(1)
        json_template = yaml.load(stream, Loader=yaml.FullLoader)

        # Basic validations
        LOG.debug("Checking template: %s",
                  json.dumps(json_template, indent=2))
        sessions = json_template.get('sessions', [])
        if len(sessions) == 0:
            LOG.error("Malformated template file. 'sessions' not defined")
            sys.exit(1)

        for window in sessions:
            LOG.debug('Looping over window: %s', window)
            if window.get('tabs') is None:
                LOG.error("No tabs detected on %s", window)
                LOG.error("Please check your syntax.")
                sys.exit(1)
            for tab_name, commands in window['tabs'].items():
                if len(commands) == 0:
                    LOG.error("No commands found for window %s tab %s",
                              window, tab_name)
                    LOG.error("Please check your syntax.")
                    sys.exit(1)

        self.sessions = sessions

    @staticmethod
    def add_args(parser):
        custom_parameters = parser.add_argument_group(CustomShells.name)
        custom_parameters.add_argument(
            "--custom-template", metavar='<template file path>',
            help='Loads windows and tab based on this template.')

    @staticmethod
    def help():
        msg = ("This template allows you to especify command sequences to be\n"
               "run in each window and tab. It reads the layout from a YAML\n"
               "file. The commands don't need to be mean to run in the local\n"
               "machine. If you ssh to another host, the next command will \n"
               "be run in that host. Bellow a snippet of the YAML format\n"
               "used: \n\n")
        msg = msg + CustomShells.print_skel() + '\n'
        return msg

