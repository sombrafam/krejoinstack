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
        def _filter_units():

            parsed_res = []
            for opt_name, re_string in [
                ("--oregex", self.configs.oregex),
                ("--noregex", self.configs.noregex)]:
                if re_string:
                    print("Compiling RE: %s" % re_string)
                    try:
                        parsed_re = re.compile(re_string)
                        print("parsed_re: %s" % parsed_re)
                        parsed_res.append(parsed_re)
                    except Exception as e:
                        print("Error parsing %s" % opt_name)
                        print(e)

            try:
                open_re = parsed_res[0]
            except Exception:
                open_re = None
                pass

            try:
                nopen_re = parsed_res[1]
            except Exception:
                nopen_re = None
                pass

            fitered_units = []
            for unit in self.units:
                print("open_re: %s" % open_re)
                print("unit: %s" % unit)
                print("match: %s" % open_re.match(unit))
                if open_re and open_re.match(unit):
                    fitered_units.append(unit)
                if nopen_re and nopen_re.match(unit):
                    fitered_units.remove(unit)

            return fitered_units

        filtered = _filter_units()
        if len(filtered) >= 1:
            for unit in filtered:
                self.konsole.new_konsole(unit)
                self.konsole.shells[unit].ssh_connect(
                    self.host, user=self.bastion_user)
                self.konsole.run(unit, 'juju ssh %s' % unit)

    @staticmethod
    def add_args(parser):
        juju_parameters = parser.add_argument_group(JujuSessions.name)
        juju_parameters.add_argument(
            "--model", help='The model to search for the units/machines.',
            metavar='<model name>')
        juju_parameters.add_argument(
            "--oregex", help='Open only units matching this regex.',
            metavar='<regex>')
        juju_parameters.add_argument(
            "--noregex",
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
