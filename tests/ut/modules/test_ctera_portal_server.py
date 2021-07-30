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

import ansible_collections.ctera.ctera.plugins.modules.ctera_portal_server as ctera_portal_server
import tests.ut.mocks.ctera_portal_base_mock as ctera_portal_base_mock
from tests.ut.base import BaseTest

try:
    from cterasdk import CTERAException
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common


class TestCteraPortalServer(BaseTest):

    def setUp(self):
        super().setUp()
        ctera_portal_base_mock.mock_bases(self, ctera_portal_server.CteraPortalServer)

    def test_get_server_doesnt_exist(self):
        server = ctera_portal_server.CteraPortalServer()
        server.parameters = dict(name='server')
        server._ctera_portal.servers.get = mock.MagicMock(side_effect=CTERAException(response=munch.Munch(code=404)))
        self.assertIsNone(server._get_server())

    def test_get_server_raise_error(self):
        server = ctera_portal_server.CteraPortalServer()
        server.parameters = dict(name='server')
        server._ctera_portal.servers.get = mock.MagicMock(side_effect=CTERAException(response=munch.Munch(code=500)))
        self.assertRaises(CTERAException, server._get_server)

    def test_get_server_exists(self):
        expected_server_dict = dict(
            server_name='server',
            app=True,
            preview=False,
            enable_public_ip=True,
            public_ip='192.168.0.1',
            allow_user_login=True,
            enable_replication=False,
            replica_of=None
        )
        server = ctera_portal_server.CteraPortalServer()
        server.parameters = dict(name='server')
        server._ctera_portal.servers.get = mock.MagicMock(
            return_value=munch.Munch(
                dict(
                    name=expected_server_dict['server_name'],
                    isApplicationServer=True,
                    renderingServer=False,
                    publicIpaddr='192.168.0.1',
                    allowUserLogin=True,
                    replicationSettings=None
                )
            )
        )
        self.assertDictEqual(expected_server_dict, server._get_server())

    def test_execute_new_name(self):
        current_name = 'server'
        new_name = 'new_name'
        server = ctera_portal_server.CteraPortalServer()
        server.parameters = dict(name=current_name, server_name=new_name)
        server._get_server = mock.MagicMock(return_value=dict(server_name=current_name))
        server._execute()
        server._ctera_portal.servers.modify.assert_called_once_with(current_name, server_name=new_name)
        self.assertTrue(server.ansible_return_value.param.changed)

    def test_execute_no_change(self):
        current_name = 'server'
        server = ctera_portal_server.CteraPortalServer()
        server.parameters = dict(name=current_name)
        server._get_server = mock.MagicMock(return_value=dict(server_name=current_name))
        server._execute()
        server._ctera_portal.servers.modify.assert_not_called()
        self.assertTrue(server.ansible_return_value.param.skipped)
