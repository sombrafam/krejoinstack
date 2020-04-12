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
import yaml
import re
import time
import sys

import krejoinstack.plugins.base as base
import krejoinstack.utils.ssh as ssh


class JujuSessions(base.KRJPlugin):
    """
        Implements krejoin stack plugin for OpenStack Juju
        TODO(erlon):
            * Check that the host has jujuc
            * Check that the host has models
    """
    name = "Juju"

    def __init__(self, args):

        super(JujuSessions, self).__init__()

        if len(args.host.split('@')) > 1:
            self.bastion_user = args.host.split('@')[0]
            self.host = args.host.split('@')[1]
        else:
            self.bastion_user = 'ubuntu'
            self.host = args.host

        self.configs = args
        # NOTE(erlon): Password based authentication not supported yet
        bastion_user_pwd = None
        self.machines, self.units = self._get_juju_info(
            self.host, self.bastion_user)

    def _find_jujuc(self, ssh_client):
        # TODO(erlon): Fix me
        return '/snap/bin/juju'

    def _get_juju_info(self, bastion_host, bastion_user='ubuntu',
                       bastion_user_pwd=''):
        print("Connecting to: %s %s %s" % (bastion_host, bastion_user, bastion_user_pwd))
        client = ssh.SSHClient(bastion_host, bastion_user, bastion_user_pwd)
        jujuc_path = self._find_jujuc(client)

        out, err = client.run('%s status' % jujuc_path)
        units_regex = '\\n((\w+-*)+/\d+)'
        units_raw = re.findall(units_regex, out.decode('utf-8'))
        units = [unit[0] for unit in units_raw]

        machines_regex = '\\n(\d+)\s'
        machines = re.findall(machines_regex, out.decode('utf-8'))

        return machines, units

    def spawn(self):
        def _spawn_targets(_targets):
            for target_dict in _targets:
                target = list(target_dict.keys())[0]
                shells = list(target_dict.values())[0].get('shells', None)
                if not shells:
                    self.konsole.new_konsole(target)
                    self.konsole.shells[target].ssh_connect(
                        self.host, user=self.bastion_user)
                    self.konsole.run(target, 'juju ssh %s' % target)
                else:

                    for command_name, command in shells.items():
                        shell_name = "%s: %s" % (target, command_name)
                        self.konsole.new_konsole(shell_name)
                        self.konsole.shells[shell_name].ssh_connect(
                            self.host, user=self.bastion_user)
                        self.konsole.run(shell_name, 'juju ssh %s' % target)
                        self.konsole.run(shell_name, command)

        def _filter_units():
            try:
                open_re = re.compile(self.configs.regex)
                print("parsed_re: %s" % open_re)
            except Exception as e:
                print("Error parsing --regex: %s" % self.configs.regex)
                print(e)
                sys.exit(1)

            fitered_units = []
            for unit in self.units:
                print("open_re: %s" % open_re)
                print("unit: %s" % unit)
                print("match: %s" % open_re.match(unit))
                if open_re and open_re.match(unit):
                    fitered_units.append(unit)

            return fitered_units

        targets = []
        if self.configs.template:
            print("Parsing template file: %s" % self.configs.template)
            stream = open(self.configs.template, 'r')
            json_template = yaml.load(stream, Loader=yaml.FullLoader)

            sessions = json_template.get('sessions', None)
            if not sessions:
                print("Malformated template file. 'sessions' not defined")
                sys.exit(1)

            template_units = sessions.get('units', [])
            template_machines = sessions.get('machines', [])

            for template_target in template_units + template_machines:
                unit_stanza = list(template_target.keys())[0]
                try:
                    compiled_stanza = re.compile(unit_stanza)
                    print("parsed_re: %s" % compiled_stanza)
                except Exception as e:
                    print("Error in stanza definition parsing %s" % unit_stanza)
                    print(e)
                    sys.exit(1)

                for model_target in self.units + self.machines:
                    if compiled_stanza.match(model_target):
                        tgt_shells = list(template_target.values())[0]
                        tgt = {model_target: tgt_shells}
                        targets.append(tgt)
        elif self.configs.regex:
            filtered = _filter_units()
            if len(filtered) >= 1:
                for unit in filtered:
                    tgt = {unit: {}}
                    targets.append(tgt)
        else:
            for unit in self.units:
                tgt = {unit: {}}
                targets.append(tgt)

        if len(targets) > 0:
            _spawn_targets(targets)
        else:
            print("Can't find any target unit or machine to open")
            sys.exit(1)

    @staticmethod
    def add_args(parser):
        juju_parameters = parser.add_argument_group(JujuSessions.name)
        # Optional: by default will use the model in context
        juju_parameters.add_argument(
            "--model", help='The model to search for the units/machines.',
            metavar='<model name>')
        # Optional: By default will open 1 tab for each selected unit/machine
        juju_parameters.add_argument(
            "--num-tabs", help='Opens N tabs for each service unit or machine.',
            metavar='<number of services>')
        # Optional: By default will open all tabs in one window. If set, each
        # application will be opened in one window.
        juju_parameters.add_argument(
            "--group-services", action='store_true',
            help='Group similar services into distict windows.')
        # Optional: Loads from a template YAML file
        juju_parameters.add_argument(
            "--template", metavar='<template file path>',
            help='Loads Juju shells based on this template.')
        # Optional: Opens only the units/machines matching to regex
        juju_parameters.add_argument(
            "--regex", help='Open only units matching this regex.',
            metavar='<regex>')
