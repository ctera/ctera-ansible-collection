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
    from cterasdk import CTERAException, gateway_types
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common

import ansible_collections.ctera.ctera.plugins.modules.ctera_filer_share as ctera_filer_share
import tests.ut.mocks.ctera_filer_base_mock as ctera_filer_base_mock
from tests.ut.base import BaseTest


class TestCteraFilerShare(BaseTest):

    def setUp(self):
        super().setUp()
        ctera_filer_base_mock.mock_bases(self, ctera_filer_share.CteraFilerShare)

    def test__execute(self):
        for is_present in [True, False]:
            self._test__execute(is_present)

    @staticmethod
    def _test__execute(is_present):
        share = ctera_filer_share.CteraFilerShare()
        share.parameters = dict(state='present' if is_present else 'absent')
        share._get_share = mock.MagicMock(return_value=dict())
        share._ensure_present = mock.MagicMock()
        share._ensure_absent = mock.MagicMock()
        share._execute()
        if is_present:
            share._ensure_present.assert_called_once_with(mock.ANY)
            share._ensure_absent.assert_not_called()
        else:
            share._ensure_absent.assert_called_once_with(mock.ANY)
            share._ensure_present.assert_not_called()

    def test_get_share_exists(self):
        expected_share_dict = dict(
            name='demo',
            directory='main/public/demo',
            acl=[],
            access='winAclMode',
            csc='manual',
            dir_permissions=777,
            comment='comment',
            export_to_afp=True,
            export_to_ftp=True,
            export_to_nfs=True,
            export_to_pc_agent=True,
            export_to_rsync=True,
            indexed=True
        )
        share_object_dict = copy.deepcopy(expected_share_dict)
        share_object_dict['volume'] = 'main'
        share_object_dict['directory'] = '/public/demo'
        share_object_dict['clientSideCaching'] = share_object_dict.pop('csc')
        share_object_dict['dirPermissions'] = share_object_dict.pop('dir_permissions')
        share_object_dict['exportToAFP'] = share_object_dict.pop('export_to_afp')
        share_object_dict['exportToFTP'] = share_object_dict.pop('export_to_ftp')
        share_object_dict['exportToNFS'] = share_object_dict.pop('export_to_nfs')
        share_object_dict['exportToPCAgent'] = share_object_dict.pop('export_to_pc_agent')
        share_object_dict['exportToRSync'] = share_object_dict.pop('export_to_rsync')
        share = ctera_filer_share.CteraFilerShare()
        share.parameters = dict(name='demo')
        share._ctera_filer.shares.get = mock.MagicMock(return_value=munch.Munch(share_object_dict))
        self.assertDictEqual(expected_share_dict, share._get_share())

    def test__get_share_doesnt_exist(self):
        share = ctera_filer_share.CteraFilerShare()
        share.parameters = dict(name='demo')
        share._ctera_filer.shares.get = mock.MagicMock(side_effect=CTERAException(response=munch.Munch(code=404)))
        self.assertIsNone(share._get_share())

    def test__get_share_failed(self):
        share = ctera_filer_share.CteraFilerShare()
        share.parameters = dict(name='demo')
        share._ctera_filer.shares.get = mock.MagicMock(side_effect=CTERAException(response=munch.Munch(code=401)))
        self.assertRaises(CTERAException, share._get_share)

    def test__to_acl_dict_local(self):
        expected_acl_dict = dict(principal_type='LocalGroup', name='Admins', perm='ReadWrite')
        acl_obj = munch.Munch(
            permissions=munch.Munch(allowedFileAccess='ReadWrite'),
            principal2=munch.Munch(
                _classname='LocalGroup',
                ref='#Admins'
            )
        )
        self.assertDictEqual(expected_acl_dict, ctera_filer_share.CteraFilerShare()._to_acl_dict(acl_obj))

    def test__to_acl_dict_domain(self):
        expected_acl_dict = dict(principal_type='DomainGroup', name='Admins', perm='ReadWrite')
        acl_obj = munch.Munch(
            permissions=munch.Munch(allowedFileAccess='ReadWrite'),
            principal2=munch.Munch(
                _classname='DomainGroup',
                name='Admins'
            )
        )
        self.assertDictEqual(expected_acl_dict, ctera_filer_share.CteraFilerShare()._to_acl_dict(acl_obj))

    def test_ensure_present(self):
        for is_present in [True, False]:
            self._test_ensure_present(is_present)

    @staticmethod
    def _test_ensure_present(is_present):
        share = ctera_filer_share.CteraFilerShare()
        share._handle_modify = mock.MagicMock()
        share._add_share = mock.MagicMock()
        share._ensure_present(share=dict(name='demo') if is_present else None)
        if is_present:
            share._handle_modify.assert_called_once_with(mock.ANY)
            share._add_share.assert_not_called()
        else:
            share._add_share.assert_called_once_with()
            share._handle_modify.assert_not_called()

    def test__add_share(self):  # pylint: disable=no-self-use
        acl_dict = dict(principal_type='LocalGroup', name='Admins', perm='ReadWrite')
        add_params = dict(
            name='demo',
            directory='/main/public/demo',
            acl=[acl_dict],
            access='winAclMode',
            csc='manual',
            dir_permissions=777,
            comment='comment',
            export_to_afp=True,
            export_to_ftp=True,
            export_to_nfs=True,
            export_to_pc_agent=True,
            export_to_rsync=True,
            indexed=True
        )
        expected_params = copy.deepcopy(add_params)
        expected_params['acl'] = mock.ANY

        share = ctera_filer_share.CteraFilerShare()
        share.parameters = add_params
        share._add_share()
        share._ctera_filer.shares.add.assert_called_with(**expected_params)
        self._verify_acl_dict(acl_dict, share._ctera_filer.shares.add.call_args[1]['acl'][0])

    def test__handle_modify(self):
        for change_attributes in [True, False]:
            self._test__handle_modify(change_attributes)

    def _test__handle_modify(self, change_attributes):
        acl_dict = dict(principal_type='LocalGroup', name='Admins', perm='ReadWrite')
        current_attributes = dict(
            name='demo',
            directory='/main/public/demo',
            acl=[acl_dict],
            access='winAclMode',
            csc='manual',
            dir_permissions=777,
            comment='comment',
            export_to_afp=True,
            export_to_ftp=True,
            export_to_nfs=True,
            export_to_pc_agent=True,
            export_to_rsync=True,
            indexed=True
        )
        desired_attributes = copy.deepcopy(current_attributes)
        if change_attributes:
            desired_acl_dict = dict(principal_type='LocalGroup', name='Everyone', perm='ReadOnly')
            desired_attributes['export_to_afp'] = False
            desired_attributes['acl'] = [desired_acl_dict]
        share = ctera_filer_share.CteraFilerShare()
        share.parameters = desired_attributes
        share._handle_modify(current_attributes)
        if change_attributes:
            share._ctera_filer.shares.modify.assert_called_with(desired_attributes['name'], export_to_afp=desired_attributes['export_to_afp'], acl=mock.ANY)
            self._verify_acl_dict(desired_acl_dict, share._ctera_filer.shares.modify.call_args[1]['acl'][0])
        else:
            share._ctera_filer.shares.modify.assert_not_called()

    def _verify_acl_dict(self, acl_dict, actual_acl):
        expected_acl = gateway_types.ShareAccessControlEntry(**acl_dict)
        self.assertEqual(expected_acl.principal_type, actual_acl.principal_type)
        self.assertEqual(expected_acl.name, actual_acl.name)
        self.assertEqual(expected_acl.perm, actual_acl.perm)

    def test_add_no_directory(self):
        share = ctera_filer_share.CteraFilerShare()
        share.parameters = dict(
            name='demo',
            acl=[],
            access='winAclMode',
            csc='manual',
            dir_permissions=777,
            comment='comment',
            export_to_afp=True,
            export_to_ftp=True,
            export_to_nfs=True,
            export_to_pc_agent=True,
            export_to_rsync=True,
            indexed=True
        )
        self.assertRaises(CTERAException, share._add_share)

    def test_ensure_absent(self):
        for is_present in [True, False]:
            self._test_ensure_absent(is_present)

    @staticmethod
    def _test_ensure_absent(is_present):
        name = 'demo'
        share = ctera_filer_share.CteraFilerShare()
        share.parameters = dict(name=name)
        share._ensure_absent(share.parameters if is_present else None)
        if is_present:
            share._ctera_filer.shares.delete.assert_called_once_with(name)
        else:
            share._ctera_filer.shares.delete.assert_not_called()
