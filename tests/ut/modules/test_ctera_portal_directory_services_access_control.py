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
    from cterasdk import CTERAException, portal_types, portal_enum
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common

import ansible_collections.ctera.ctera.plugins.modules.ctera_portal_directory_services_access_control as ctera_portal_access_control
import tests.ut.mocks.ctera_portal_base_mock as ctera_portal_base_mock
from tests.ut.base import BaseTest

try:
    from cterasdk import CTERAException
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common


class TestCteraPortalDirectoryServicesAccessControl(BaseTest):

    def setUp(self):
        super().setUp()
        self._current_acl = [
            portal_types.AccessControlEntry(portal_types.UserAccount('jsmith', 'demo.local'), portal_enum.Role.ReadWriteAdmin),
            portal_types.AccessControlEntry(portal_types.GroupAccount('Users', 'demo.local'), portal_enum.Role.EndUser)
        ]
        ctera_portal_base_mock.mock_bases(self, ctera_portal_access_control.CteraPortalDirectoryServicesAccessControl)

    def test_ensure_absent_changed(self):
        access_control = ctera_portal_access_control.CteraPortalDirectoryServicesAccessControl()
        access_control._ensure_absent(munch.Munch(dict(name='test')))
        access_control._ctera_portal.directoryservice.set_access_control.assert_called_once_with([])
        self.assertTrue(access_control.ansible_return_value.param.changed)
        self.assertEqual(access_control.ansible_return_value.param.msg, 'Removed access control entries')

    def test_ensure_absent_skipped(self):
        access_control = ctera_portal_access_control.CteraPortalDirectoryServicesAccessControl()
        access_control._ensure_absent(None)
        access_control._ctera_portal.directoryservice.set_access_control.assert_not_called()
        self.assertTrue(access_control.ansible_return_value.param.skipped)
        self.assertEqual(access_control.ansible_return_value.param.msg, 'No access control rules exist')

    def test_execute_present_changed(self):
        access_control = ctera_portal_access_control.CteraPortalDirectoryServicesAccessControl()
        access_control._ctera_portal.directoryservice.get_access_control = mock.MagicMock(return_value=self._current_acl)
        admin = dict(principal_type='user', name='jsara', domain='demo.local', role='ReadWriteAdmin')
        ro_admin_group = dict(principal_type='group', name='Administrators', domain='demo.local', role='ReadOnlyAdmin')
        access_control.parameters = dict(state='present', acl=[admin, ro_admin_group])
        access_control._execute()
        access_control._ctera_portal.directoryservice.set_access_control.assert_called_once_with(mock.ANY)
        acl = access_control._ctera_portal.directoryservice.set_access_control.call_args[0][0]
        self.assertEqual(len(acl), len([admin, ro_admin_group]))
        for ace in acl:
            if ace.account.account_type == 'user':
                user = self._dict_to_ace(admin)
                self.assertEqual(ace.role, user.role)
                self.assertEqual(ace.account, user.account)
            if ace.account.account_type == 'group':
                group = self._dict_to_ace(ro_admin_group)
                self.assertEqual(ace.role, group.role)
                self.assertEqual(ace.account, group.account)
        self.assertTrue(access_control.ansible_return_value.param.changed)
        self.assertEqual(access_control.ansible_return_value.param.msg, 'Configured access control rules')

    def test_execute_present_skipped(self):
        access_control = ctera_portal_access_control.CteraPortalDirectoryServicesAccessControl()
        access_control._ctera_portal.directoryservice.get_access_control = mock.MagicMock(return_value=self._current_acl)
        admin = dict(principal_type='user', name='jsmith', domain='demo.local', role='ReadWriteAdmin')
        end_users = dict(principal_type='group', name='Users', domain='demo.local', role='EndUser')
        access_control.parameters = dict(state='present', acl=[admin, end_users])
        access_control._execute()
        self.assertTrue(access_control.ansible_return_value.param.skipped)
        self.assertEqual(access_control.ansible_return_value.param.msg, 'Access control details did not change')

    def test_get_acl_not_found(self):
        access_control = ctera_portal_access_control.CteraPortalDirectoryServicesAccessControl()
        access_control._ctera_portal.directoryservice.get_access_control = mock.MagicMock(side_effect=CTERAException(response=munch.Munch(code=500)))
        self.assertRaises(CTERAException, access_control._get_access_control_rules)

    def test_invalid_principal_type(self):
        access_control = ctera_portal_access_control.CteraPortalDirectoryServicesAccessControl()
        self.assertRaises(CTERAException, access_control._create_access_control_entries, [
                dict(principal_type='invalid', domain='demo.local', name='test', role='ReadWriteAdmin')
            ]
        )

    def test_execute_ensure_absent(self):
        access_control = ctera_portal_access_control.CteraPortalDirectoryServicesAccessControl()
        access_control._get_access_control_rules = mock.MagicMock(return_value=self._current_acl)
        access_control._create_access_control_entries = mock.MagicMock()
        access_control._create_access_control_index = mock.MagicMock()
        access_control._ensure_absent = mock.MagicMock()
        access_control.parameters = dict(state='absent', acl='test')
        access_control._execute()
        access_control._ensure_absent.assert_called_once_with(self._current_acl)

    def _dict_to_ace(self, array):
        if array['principal_type'] == 'user':
            return portal_types.AccessControlEntry(portal_types.UserAccount(array['name'], array['domain']), array['role'])
        if array['principal_type'] == 'group':
            return portal_types.AccessControlEntry(portal_types.GroupAccount(array['name'], array['domain']), array['role'])
        return None
