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

import unittest.mock as mock
import munch

import ansible_collections.ctera.ctera.plugins.modules.ctera_filer_snmp as ctera_filer_snmp
import tests.ut.mocks.ctera_filer_base_mock as ctera_filer_base_mock
from tests.ut.base import BaseTest


class TestCteraFilerSNMP(BaseTest):

    def setUp(self):
        super().setUp()
        self._community_str = 'community'
        self._port=8161
        self._username = 'user'
        self._password = 'pass'
        ctera_filer_base_mock.mock_bases(self, ctera_filer_snmp.CteraFilerSNMP)

    def test_enable_snmp(self):
        snmp = ctera_filer_snmp.CteraFilerSNMP()
        snmp.parameters = dict(
            enabled=True,
            port=self._port,
            community_str=self._community_str,
            username=self._username,
            password=self._password,
            update_password=False
        )
        snmp._ctera_filer.snmp.is_enabled = mock.MagicMock(return_value=False)
        snmp._ctera_filer.snmp.enable = mock.MagicMock()
        snmp._execute()
        snmp._ctera_filer.snmp.is_enabled.assert_called_once()
        snmp._ctera_filer.snmp.enable.assert_called_once_with(port=self._port, community_str=self._community_str,
                                                              username=self._username, password=self._password)
        self.assertTrue(snmp.ansible_return_value.param.changed)

    def test_disable_snmp(self):
        for is_enabled in [True, False]:
            self._test_disable_snmp(is_enabled)

    def _test_disable_snmp(self, is_enabled):
        snmp = ctera_filer_snmp.CteraFilerSNMP()
        snmp.parameters = dict(
            enabled=False
        )
        snmp._ctera_filer.snmp.is_enabled = mock.MagicMock(return_value=is_enabled)
        snmp._ctera_filer.snmp.disable = mock.MagicMock()
        snmp._execute()
        snmp._ctera_filer.snmp.is_enabled.assert_called_once()
        if is_enabled:
            snmp._ctera_filer.snmp.disable.assert_called_once()
            self.assertTrue(snmp.ansible_return_value.param.changed)
        else:
            snmp._ctera_filer.snmp.disable.assert_not_called()
            self.assertTrue(snmp.ansible_return_value.param.skipped)

    def test_modify_snmp(self):
        for changed in [True, False]:
            self._test_modify_snmp(changed)

    def _test_modify_snmp(self, changed):
        snmp = ctera_filer_snmp.CteraFilerSNMP()
        snmp.parameters = dict(
            enabled=True,
            port=self._port,
            community_str=self._community_str,
            update_password=False
        )
        snmp._ctera_filer.snmp.is_enabled = mock.MagicMock(return_value=True)
        snmp_config = munch.Munch(port=161, readCommunity='random', snmpV3=None) if changed else munch.Munch(port=self._port, readCommunity=self._community_str, snmpV3=None)
        snmp._ctera_filer.snmp.get_configuration = mock.MagicMock(return_value=snmp_config)
        snmp._ctera_filer.snmp.modify = mock.MagicMock()
        snmp._execute()
        snmp._ctera_filer.snmp.is_enabled.assert_called_once()
        if changed:
            snmp._ctera_filer.snmp.modify.assert_called_once_with(port=self._port, community_str=self._community_str)
            self.assertTrue(snmp.ansible_return_value.param.changed)
        else:
            snmp._ctera_filer.snmp.modify.assert_not_called()
            self.assertTrue(snmp.ansible_return_value.param.skipped)
