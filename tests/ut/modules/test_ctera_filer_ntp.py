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

import ansible_collections.ctera.ctera.plugins.modules.ctera_filer_ntp as ctera_filer_ntp
import tests.ut.mocks.ctera_filer_base_mock as ctera_filer_base_mock
from tests.ut.base import BaseTest


class TestCteraFilerNtp(BaseTest):

    def setUp(self):
        super().setUp()
        ctera_filer_base_mock.mock_bases(self, ctera_filer_ntp.CteraFilerNtp)

    def test__execute(self):
        for is_enabled in [True, False]:
            self._test__execute(is_enabled)

    @staticmethod
    def _test__execute(is_enabled):
        ntp = ctera_filer_ntp.CteraFilerNtp()
        ntp.parameters = dict(state='enabled' if is_enabled else 'disabled')
        current_config_dict = dict()
        ntp._ctera_filer.ntp.get_configuration = mock.MagicMock(return_value=current_config_dict)
        ntp._ensure_enabled = mock.MagicMock()
        ntp._ensure_disabled = mock.MagicMock()
        ntp._execute()
        if is_enabled:
            ntp._ensure_enabled.assert_called_once_with(current_config_dict)
            ntp._ensure_disabled.assert_not_called()
        else:
            ntp._ensure_disabled.assert_called_once_with(current_config_dict)
            ntp._ensure_enabled.assert_not_called()

    def test__ensure_enabled(self):
        for current_is_enabled in [True, False]:
            for change_attributes in [True, False]:
                self._test__ensure_enabled(current_is_enabled, change_attributes)

    @staticmethod
    def _test__ensure_enabled(current_is_enabled, change_attributes):
        ntp = ctera_filer_ntp.CteraFilerNtp()
        current_config = dict(
            NTPMode='enabled' if current_is_enabled else 'disabled',
            NTPServer=['0.pool.ntp.org']
        )
        ntp_servers = current_config['NTPServer']
        if change_attributes:
            ntp_servers = ['1.pool.ntp.org']
        ntp.parameters = dict(servers=ntp_servers)
        ntp._ensure_enabled(munch.Munch(current_config))
        if current_is_enabled:
            if change_attributes:
                ntp._ctera_filer.ntp.enable.assert_called_once_with(ntp_servers)
            else:
                ntp._ctera_filer.ntp.enable.assert_not_called()
        else:
            ntp._ctera_filer.ntp.enable.assert_called_once_with(ntp_servers)

    def test__ensure_disabled(self):
        for current_is_enabled in [True, False]:
            self._test__ensure_disabled(current_is_enabled)

    @staticmethod
    def _test__ensure_disabled(current_is_enabled):
        ntp = ctera_filer_ntp.CteraFilerNtp()
        current_config = dict(
            NTPMode='enabled' if current_is_enabled else 'disabled'
        )
        ntp._ensure_disabled(munch.Munch(current_config))
        if current_is_enabled:
            ntp._ctera_filer.ntp.disable.assert_called_once()
        else:
            ntp._ctera_filer.ntp.disable.assert_not_called()
