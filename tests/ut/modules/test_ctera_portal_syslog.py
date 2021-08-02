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

try:
    from cterasdk import CTERAException
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common

import ansible_collections.ctera.ctera.plugins.modules.ctera_portal_syslog as ctera_portal_syslog
import tests.ut.mocks.ctera_portal_base_mock as ctera_portal_base_mock
from tests.ut.base import BaseTest

try:
    from cterasdk import CTERAException
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common


class TestCteraPortalSyslog(BaseTest):

    def setUp(self):
        super().setUp()
        ctera_portal_base_mock.mock_bases(self, ctera_portal_syslog.CteraPortalSyslog)

    def test_get_current_syslog_config(self):
        syslog = ctera_portal_syslog.CteraPortalSyslog()
        server = '192.168.0.1'
        port = 514
        min_severity = 'info'
        expected_server_dict = dict(
            server=server,
            port=port,
            min_severity=min_severity
        )
        syslog._ctera_portal.syslog.get_configuration = mock.MagicMock(return_value=munch.Munch(server=server, port=port, minSeverity=min_severity))
        self.assertDictEqual(expected_server_dict, syslog._get_current_syslog_config())

    def test_execute(self):
        syslog = ctera_portal_syslog.CteraPortalSyslog()
        syslog._ensure_enabled = mock.MagicMock()
        syslog._ensure_disabled = mock.MagicMock()
        for state in ['enabled', 'disabled']:
            syslog.parameters = dict(state=state)
            syslog._execute()
            if state == 'enabled':
                syslog._ensure_enabled.assert_called_once()
            else:
                syslog._ensure_disabled.assert_called_once()

    def test_modify(self):
        current_server = '192.168.0.1'
        new_server = '192.168.0.2'
        syslog = ctera_portal_syslog.CteraPortalSyslog()
        syslog._get_current_syslog_config = mock.MagicMock(return_value=dict(server=current_server))
        syslog.parameters = dict(server=new_server)
        syslog._ensure_enabled()
        syslog._ctera_portal.syslog.modify.assert_called_once_with(server=new_server)
        self.assertTrue(syslog.ansible_return_value.param.changed)
        self.assertEqual(syslog.ansible_return_value.param.msg, 'Syslog server configuration was modified')

    def test_ensure_enabled(self):
        server = '192.168.0.1'
        syslog = ctera_portal_syslog.CteraPortalSyslog()
        syslog._get_current_syslog_config = mock.MagicMock(return_value=dict(server=server))
        syslog.parameters = dict(server=server)
        for is_enabled in [True, False]:
            syslog._ctera_portal.syslog.is_enabled = mock.MagicMock(return_value=is_enabled)
            syslog._ensure_enabled()
            if is_enabled:
                self.assertTrue(syslog.ansible_return_value.param.skipped)
                self.assertEqual(syslog.ansible_return_value.param.msg, 'Syslog server config did not change')
            else:
                syslog._ctera_portal.syslog.enable.assert_called_once_with(server)
                self.assertTrue(syslog.ansible_return_value.param.changed)
                self.assertEqual(syslog.ansible_return_value.param.msg, 'Syslog server enabled')

    def test_ensure_disabled(self):
        syslog = ctera_portal_syslog.CteraPortalSyslog()
        for is_enabled in [True, False]:
            syslog._ctera_portal.syslog.is_enabled = mock.MagicMock(return_value=is_enabled)
            syslog._ensure_disabled()
            if is_enabled:
                syslog._ctera_portal.syslog.disable.assert_called_once()
                self.assertTrue(syslog.ansible_return_value.param.changed)
                self.assertEqual(syslog.ansible_return_value.param.msg, 'Syslog server disabled')
            else:
                self.assertTrue(syslog.ansible_return_value.param.skipped)
                self.assertEqual(syslog.ansible_return_value.param.msg, 'Syslog server is already disabled')
