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

import ansible_collections.ctera.ctera.plugins.modules.ctera_filer_syslog as ctera_filer_syslog
import tests.ut.mocks.ctera_filer_base_mock as ctera_filer_base_mock
from tests.ut.base import BaseTest


class TestCteraFilerSyslog(BaseTest):

    def setUp(self):
        super().setUp()
        ctera_filer_base_mock.mock_bases(self, ctera_filer_syslog.CteraFilerSyslog)

    def test__execute(self):
        for is_enabled in [True, False]:
            self._test__execute(is_enabled)

    @staticmethod
    def _test__execute(is_enabled):
        syslog = ctera_filer_syslog.CteraFilerSyslog()
        syslog.parameters = dict(enabled=is_enabled)
        current_config_dict = dict(mode='enabled')
        syslog._get_current_config = mock.MagicMock(return_value=current_config_dict)
        syslog._ensure_enabled = mock.MagicMock()
        syslog._ensure_disabled = mock.MagicMock()
        syslog._execute()
        if is_enabled:
            syslog._ensure_enabled.assert_called_once_with(current_config_dict)
            syslog._ensure_disabled.assert_not_called()
        else:
            syslog._ensure_disabled.assert_called_once_with(current_config_dict)
            syslog._ensure_enabled.assert_not_called()

    def test__ensure_enabled(self):
        for current_is_enabled in [True, False]:
            for change_attributes in [True, False]:
                self._test__ensure_enabled(current_is_enabled, change_attributes)

    @staticmethod
    def _test__ensure_enabled(current_is_enabled, change_attributes):
        syslog = ctera_filer_syslog.CteraFilerSyslog()
        current_config = dict(
            mode='enabled' if current_is_enabled else 'disabled',
            server='192.168.1.1',
            port=514,
            proto='UDP',
            min_severity='info'
        )
        parameters_dict = copy.deepcopy(current_config)
        if change_attributes:
            parameters_dict['server'] = '192.168.1.2'
        syslog.parameters = parameters_dict
        syslog._ensure_enabled(current_config)
        if current_is_enabled:
            if change_attributes:
                syslog._ctera_filer.syslog.modify.assert_called_once_with(server='192.168.1.2')
            else:
                syslog._ctera_filer.syslog.modify.assert_not_called()
        else:
            enable_params = copy.deepcopy(parameters_dict)
            enable_params.pop('mode')
            syslog._ctera_filer.syslog.enable.assert_called_once_with(**enable_params)

    def test__ensure_disaled(self):
        for current_is_enabled in [True, False]:
            self._test__ensure_disabled(current_is_enabled)

    @staticmethod
    def _test__ensure_disabled(current_is_enabled):
        syslog = ctera_filer_syslog.CteraFilerSyslog()
        current_config = dict(
            mode='enabled' if current_is_enabled else 'disabled'
        )
        syslog._ensure_disabled(current_config)
        if current_is_enabled:
            syslog._ctera_filer.syslog.disable.assert_called_once_with()
        else:
            syslog._ctera_filer.syslog.disable.assert_not_called()

    def test__get_current_config(self):
        expected_dict = dict(
            mode='enabled',
            server='192.168.1.1',
            port=514,
            proto='UDP',
            min_severity='info'
        )
        config_dict = copy.deepcopy(expected_dict)
        config_dict['minSeverity'] = config_dict.pop('min_severity')
        syslog = ctera_filer_syslog.CteraFilerSyslog()
        syslog._ctera_filer.syslog.get_configuration.return_value = munch.Munch(config_dict)
        self.assertDictEqual(expected_dict, syslog._get_current_config())
