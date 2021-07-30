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

import ansible_collections.ctera.ctera.plugins.modules.ctera_filer_directory_services as ctera_filer_directory_services
import tests.ut.mocks.ctera_filer_base_mock as ctera_filer_base_mock
from tests.ut.base import BaseTest


class TestCteraFilerDirectoryServices(BaseTest):

    def setUp(self):
        super().setUp()
        ctera_filer_base_mock.mock_bases(self, ctera_filer_directory_services.CteraFilerDirectoryServices)

    def test__execute(self):
        for is_connected in [True, False]:
            for desired in [True, False]:
                self._test__execute(is_connected, desired)

    @staticmethod
    def _test__execute(is_connected, desired):
        domain_dict = dict(domain='example.com' if is_connected else '')
        directory_services = ctera_filer_directory_services.CteraFilerDirectoryServices()
        directory_services._ctera_filer.directoryservice.get_connected_domain.return_value = munch.Munch(domain_dict)
        directory_services.parameters = dict(state='connected' if desired else 'disconnected')
        directory_services._ensure_connected = mock.MagicMock()
        directory_services._ensure_disconnected = mock.MagicMock()
        directory_services._execute()
        if desired:
            directory_services._ensure_connected.assert_called_once_with(domain_dict)
            directory_services._ensure_disconnected.assert_not_called()
        else:
            directory_services._ensure_connected.assert_not_called()
            directory_services._ensure_disconnected.assert_called_once_with(domain_dict)

    def test__ensure_connected(self):
        for is_connected in [True, False]:
            self._test__ensure_connected(is_connected)

    @staticmethod
    def _test__ensure_connected(is_connected):
        domain_dict = dict(domain='example.com' if is_connected else '')
        directory_services = ctera_filer_directory_services.CteraFilerDirectoryServices()
        directory_services._handle_modify = mock.MagicMock()
        directory_services._do_connect = mock.MagicMock()
        directory_services._ensure_connected(domain_dict)
        if is_connected:
            directory_services._handle_modify.assert_called_once_with(domain_dict)
            directory_services._do_connect.assert_not_called()
        else:
            directory_services._handle_modify.assert_not_called()
            directory_services._do_connect.assert_called_once_with()

    def test__do_connect(self):
        connect_parameters = dict(domain='example.com', username='admin', password='password')
        directory_services = ctera_filer_directory_services.CteraFilerDirectoryServices()
        directory_services.parameters = copy.deepcopy(connect_parameters)
        directory_services.parameters['unused_param'] = True
        directory_services._do_connect()
        directory_services._ctera_filer.directoryservice.connect.assert_called_once_with(**connect_parameters)
        self.assertEqual(directory_services.ansible_return_value.param.msg, 'Connected to Active Directory')
        self.assertTrue(directory_services.ansible_return_value.param.changed)

    def test__handle_modify(self):
        for change_domain in [True, False]:
            for force_reconnect in [True, False]:
                self._test__handle_modify(change_domain, force_reconnect)

    def _test__handle_modify(self, change_domain, force_reconnect):
        current_domain_name = 'example.com'
        new_domain_name = 'new.com'
        directory_services = ctera_filer_directory_services.CteraFilerDirectoryServices()
        directory_services.parameters = dict(
            domain=new_domain_name if change_domain else current_domain_name,
            force_reconnect=force_reconnect
        )
        directory_services._do_connect = mock.MagicMock()
        directory_services._handle_modify(dict(domain=current_domain_name))
        if (not change_domain) and (not force_reconnect):
            directory_services._ctera_filer.directoryservice.disconnect.assert_not_called()
            directory_services._do_connect.assert_not_called()
            self.assertEqual(directory_services.ansible_return_value.param.msg, 'The Edge Filer is already connected to Active Directory')
        else:
            directory_services._ctera_filer.directoryservice.disconnect.assert_called_once_with()
            directory_services._do_connect.assert_called_once_with()

    def test__ensure_disconnected(self):
        for is_connected in [True, False]:
            self._test__ensure_disconnected(is_connected)

    def _test__ensure_disconnected(self, is_connected):
        domain_dict = dict(domain='example.com' if is_connected else '')
        directory_services = ctera_filer_directory_services.CteraFilerDirectoryServices()
        directory_services._ensure_disconnected(domain_dict)
        if is_connected:
            directory_services._ctera_filer.directoryservice.disconnect.assert_called_once_with()
            self.assertEqual(directory_services.ansible_return_value.param.msg, 'Successfully disconnected the Edge Filer the Active Directory')
            self.assertTrue(directory_services.ansible_return_value.param.changed)
        else:
            directory_services._ctera_filer.directoryservice.disconnect.assert_not_called()
            self.assertEqual(directory_services.ansible_return_value.param.msg, 'The Edge Filer is already not connected to Active Directory')
