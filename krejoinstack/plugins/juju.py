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
import re
import time

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

        host = args.host.split('@')[0]
        if len(args.host.split('@')) > 1:
            bastion_user = args.host.split('@')[1]
        else:
            bastion_user = 'ubuntu'

        # NOTE(erlon): Password based authentication not supported yet
        bastion_user_pwd = None
        self.machines, self.units = self._get_juju_info(
            host, bastion_user, bastion_user_pwd)

    def _find_jujuc(self, ssh_client):
        # TODO(erlon): Fix me
        return '/snap/bin/juju'

    def _get_juju_info(self, bastion_host, bastion_user='ubuntu',
                       bastion_user_pwd=''):
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
        for unit in self.units:
            self.konsole.new_konsole(unit)
            #time.sleep(0.2)

    @staticmethod
    def add_args(parser):
        juju_parameters = parser.add_argument_group(JujuSessions.name)
        juju_parameters.add_argument(
            "--model", help='The model to search for the units/machines.',
            metavar='<model name>')
        juju_parameters.add_argument(
            "--open-regex", help='Open only units matching this regex.',
            metavar='<regex>')
        juju_parameters.add_argument(
            "--no-open-regex",
            help='Open only units not mathiching this regex.',
            metavar='<regex>')
        juju_parameters.add_argument(
            "--num-services", help='Opens N tabs for each service.',
            metavar='<number of services>')
        juju_parameters.add_argument(
            "--group-services", action='store_true',
            help='Group similar services into distict windows.')
        juju_parameters.add_argument(
            "--machines", metavar='<list of juju machines>',
            help='Also logs into the listed machines.')
        juju_parameters.add_argument(
            "--template", metavar='<template file path>',
            help='Loads Juju shells based on this template.')
