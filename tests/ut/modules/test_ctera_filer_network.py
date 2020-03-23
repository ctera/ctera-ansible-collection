# pylint: disable=protected-access

# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is licensed under the Apache License 2.0.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# Copyright 2020, CTERA Networks
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import copy
import unittest.mock as mock
import munch

import ansible_collections.ctera.ctera.plugins.modules.ctera_filer_network as ctera_filer_network
import tests.ut.mocks.ctera_filer_base_mock as ctera_filer_base_mock
from tests.ut.base import BaseTest


class TestCteraFilerNetwork(BaseTest):
    _mode_options = ['dynamic', 'static']

    def setUp(self):
        super().setUp()
        ctera_filer_base_mock.mock_bases(self, ctera_filer_network.CteraFilerNetwork)

    def test__execute(self):
        for current_mode in TestCteraFilerNetwork._mode_options:
            for desired_mode in TestCteraFilerNetwork._mode_options:
                self._test__execute(current_mode, desired_mode)

    @staticmethod
    def _test__execute(current_mode, desired_mode):
        network = ctera_filer_network.CteraFilerNetwork()
        network.parameters = dict(mode=desired_mode)
        current_config_dict = dict(mode=current_mode)
        network._get_current_config = mock.MagicMock(return_value=current_config_dict)
        network._ensure_dynamic = mock.MagicMock()
        network._ensure_static = mock.MagicMock()
        network._execute()
        if desired_mode == 'dynamic':
            network._ensure_dynamic.assert_called_once_with(current_config_dict)
            network._ensure_static.assert_not_called()
        else:
            network._ensure_static.assert_called_once_with(current_config_dict)
            network._ensure_dynamic.assert_not_called()

    def test__ensure_dynamic(self):
        for current_mode in TestCteraFilerNetwork._mode_options:
            for primary_dns_server in [None, '8.8.8.8']:
                self._test__ensure_dynamic(current_mode, primary_dns_server)

    @staticmethod
    def _test__ensure_dynamic(current_mode, primary_dns_server):
        network = ctera_filer_network.CteraFilerNetwork()
        network.parameters = dict(primary_dns_server=primary_dns_server)
        current_config_dict = dict(mode=current_mode)
        network._ensure_dns_servers = mock.MagicMock()
        network._ensure_dynamic(current_config_dict)
        if current_mode == 'dynamic':
            network._ctera_filer.network.enable_dhcp.assert_not_called()
        else:
            network._ctera_filer.network.enable_dhcp.assert_called_once_with()
        if primary_dns_server:
            network._ensure_dns_servers.assert_called_once_with(current_config_dict, mock.ANY)
        else:
            network._ensure_dns_servers.assert_not_called()

    def test__ensure_dns_servers(self):
        for change_primary in [True, False]:
            for change_secondary in [True, False]:
                self._test__ensure_dns_servers(change_primary, change_secondary)

    def _test__ensure_dns_servers(self, change_primary, change_secondary):
        current_primary = 'current_primary'
        desired_primary = 'desired_primary' if change_primary else current_primary
        current_secondary = 'current_secondary'
        desired_secondary = 'desired_secondary' if change_secondary else current_secondary
        network = ctera_filer_network.CteraFilerNetwork()
        network.parameters = dict(primary_dns_server=desired_primary, secondary_dns_server=desired_secondary)
        current_config_dict = dict(primary_dns_server=current_primary, secondary_dns_server=current_secondary)
        messages = dict(changed=[], skipped=[])
        network._ensure_dns_servers(current_config_dict, messages)
        if change_primary or change_secondary:
            network._ctera_filer.network.set_static_nameserver.assert_called_once_with(desired_primary, secondary_dns_server=desired_secondary)
            self.assertEqual(messages['changed'], ['DNS Servers were set'])
        else:
            network._ctera_filer.network.set_static_nameserver.assert_not_called()
            self.assertEqual(messages['skipped'], ['DNS Servers did not change'])

    def test__ensure_static(self):
        for current_mode in TestCteraFilerNetwork._mode_options:
            for change_attributes in [True, False]:
                self._test__ensure_static(current_mode, change_attributes)

    @staticmethod
    def _test__ensure_static(current_mode, change_attributes):
        desired_config = dict(
            address='192.168.1.1',
            subnet='255.255.255.0',
            gateway='192.168.1.2',
            primary_dns_server='192.168.1.3'
        )
        if current_mode == 'dynamic':
            current_config_dict = dict(mode=current_mode)
        else:
            current_config_dict = copy.deepcopy(desired_config)
            current_config_dict['mode'] = current_mode
            if change_attributes:
                current_config_dict['address'] = '192.168.1.10'
        network = ctera_filer_network.CteraFilerNetwork()
        network.parameters = desired_config
        network._ensure_static(current_config_dict)
        if current_mode == 'dynamic' or change_attributes:
            network._ctera_filer.network.set_static_ipaddr.assert_called_once_with(**desired_config)
        else:
            network._ctera_filer.network.set_static_ipaddr.assert_not_called()

    def test__get_current_config(self):
        expected_dict = dict(
            mode='static',
            address='192.168.1.1',
            subnet='255.255.255.0',
            gateway='192.168.1.2',
            primary_dns_server='192.168.1.3',
            secondary_dns_server='192.168.1.4'
        )
        config_object = munch.Munch(
            DHCPMode='disabled',
            address=expected_dict['address'],
            netmask=expected_dict['subnet'],
            gateway=expected_dict['gateway'],
            DNSServer1=expected_dict['primary_dns_server'],
            DNSServer2=expected_dict['secondary_dns_server']
        )
        network = ctera_filer_network.CteraFilerNetwork()
        network._ctera_filer.network.ifconfig.return_value = munch.Munch(ip=config_object)
        self.assertDictEqual(expected_dict, network._get_current_config())
