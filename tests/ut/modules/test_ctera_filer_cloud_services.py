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

try:
    from cterasdk import config, CTERAException
except ImportError:  # pragma: no cover
    pass

import ansible_collections.ctera.ctera.plugins.modules.ctera_filer_cloud_services as ctera_filer_cloud_services
import tests.ut.mocks.ctera_filer_base_mock as ctera_filer_base_mock
from tests.ut.base import BaseTest


class TestCteraFilerCloudServices(BaseTest):

    def setUp(self):
        super().setUp()
        ctera_filer_base_mock.mock_bases(self, ctera_filer_cloud_services.CteraFilerCloudServices)

    def test__execute(self):
        default_ssl_configuration = config.connect['ssl']
        for state in ['connected', 'disconnected']:
            for trust_certificate in [True, False]:
                for is_connected in [True, False]:
                    # Reset SSL configuration to default
                    config.connect['ssl'] = default_ssl_configuration
                    self._test__execute(state, trust_certificate, is_connected, default_ssl_configuration)


    def _test__execute(self, state, trust_certificate, is_connected, default_ssl_configuration):
        status = munch.Munch(dict(connected=is_connected))
        cloud_cache = ctera_filer_cloud_services.CteraFilerCloudServices()
        cloud_cache.parameters = dict(state=state, trust_certificate=trust_certificate, server='test.example.com')
        cloud_cache._ctera_filer.services.get_status.return_value = status
        cloud_cache._ensure_connected = mock.MagicMock()
        cloud_cache._execute()
        self.assertEqual('Trust' if trust_certificate else default_ssl_configuration, config.connect['ssl'])
        if state == 'connected':
            cloud_cache._ensure_connected.assert_called_once_with(status)
        else:
            if is_connected:
                cloud_cache._ctera_filer.services.disconnect.assert_called_once_with()
            else:
                cloud_cache._ctera_filer.services.disconnect.assert_not_called()

    def test__ensure_connected(self):
        for is_connected in [True, False]:
            for modify_return in [True, False]:
                self._test__ensure_connected(is_connected, modify_return)

    @staticmethod
    def _test__ensure_connected(is_connected, modify_return):
        status = munch.Munch(dict(connected=is_connected))
        cloud_cache = ctera_filer_cloud_services.CteraFilerCloudServices()
        cloud_cache.parameters = dict(server='test.example.com')
        cloud_cache._handle_modify = mock.MagicMock(return_value=modify_return)
        cloud_cache._do_connect = mock.MagicMock()
        cloud_cache._ensure_sso_state = mock.MagicMock()
        cloud_cache._ensure_connected(status)
        if is_connected:
            cloud_cache._handle_modify.assert_called_once_with(status, mock.ANY)
            cloud_cache._do_connect.assert_not_called()
        else:
            cloud_cache._handle_modify.assert_not_called()
            cloud_cache._do_connect.assert_called_once_with()
        if is_connected and not modify_return:
            cloud_cache._ensure_sso_state.assert_not_called()
        else:
            cloud_cache._ensure_sso_state.assert_called_once_with(mock.ANY)

    def test__ensure_sso_state(self):
        for is_sso_enabled in [True, False]:
            for desired_sso_state in [True, False]:
                self._test__ensure_sso_state(is_sso_enabled, desired_sso_state)

    @staticmethod
    def _test__ensure_sso_state(is_sso_enabled, desired_sso_state):
        cloud_cache = ctera_filer_cloud_services.CteraFilerCloudServices()
        cloud_cache.parameters = dict(sso=desired_sso_state)
        cloud_cache._ctera_filer.services.sso_enabled.return_value = is_sso_enabled
        cloud_cache._ensure_sso_state(dict(changed=[], skipped=[]))
        if is_sso_enabled == desired_sso_state:
            cloud_cache._ctera_filer.services.enable_sso.assert_not_called()
            cloud_cache._ctera_filer.services.disable_sso.assert_not_called()
        elif desired_sso_state:
            cloud_cache._ctera_filer.services.enable_sso.assert_called_once_with()
            cloud_cache._ctera_filer.services.disable_sso.assert_not_called()
        else:
            cloud_cache._ctera_filer.services.enable_sso.assert_not_called()
            cloud_cache._ctera_filer.services.disable_sso.assert_called_once_with()

    @staticmethod
    def test_do_connect():
        connect_parameters = dict(server='test.example.com', user='admin', password='password')
        cloud_cache = ctera_filer_cloud_services.CteraFilerCloudServices()
        cloud_cache.parameters = copy.deepcopy(connect_parameters)
        cloud_cache.parameters['unused_param'] = True
        cloud_cache._do_connect()
        cloud_cache._ctera_filer.services.connect.assert_called_once_with(**connect_parameters)

    def test__handle_modify(self):
        for change_server in [True, False]:
            for connect_success in [True, False]:
                for force_reconnect in [True, False]:
                    self._test__handle_modify(change_server, connect_success, force_reconnect)

    def _test__handle_modify(self, change_server, connect_success, force_reconnect):
        current_server = 'current_server'
        other_server = 'other_server'
        status = munch.Munch(dict(server_address=current_server))
        cloud_cache = ctera_filer_cloud_services.CteraFilerCloudServices()
        cloud_cache.parameters = dict(server=other_server if change_server else current_server, force_reconnect=force_reconnect)
        cloud_cache._do_connect = mock.MagicMock()
        if not connect_success:
            cloud_cache._do_connect.side_effect = CTERAException()
        ret = cloud_cache._handle_modify(status, dict(changed=[], skipped=[]))
        if change_server:
            cloud_cache._ctera_filer.services.disconnect.assert_called_once_with()
            cloud_cache._do_connect.assert_called_once_with()
            self.assertEqual(ret, connect_success)
        else:
            if force_reconnect:
                cloud_cache._ctera_filer.services.reconnect.assert_called_once_with()
            else:
                cloud_cache._ctera_filer.services.reconnect.assert_not_called()
            self.assertTrue(ret)
