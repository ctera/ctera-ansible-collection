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
import datetime
import unittest.mock as mock
import munch

try:
    from cterasdk import CTERAException, portal_types
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common

import ansible_collections.ctera.ctera.plugins.modules.ctera_portal_tenant as ctera_portal_tenant
import tests.ut.mocks.ctera_portal_base_mock as ctera_portal_base_mock
from tests.ut.base import BaseTest


class TestCteraPortalTenant(BaseTest):

    def setUp(self):
        super().setUp()
        ctera_portal_base_mock.mock_bases(self, ctera_portal_tenant.CteraPortalTenant)

    def test__execute(self):
        for is_present in [True, False]:
            self._test__execute(is_present)

    @staticmethod
    def _test__execute(is_present):
        tenant = ctera_portal_tenant.CteraPortalTenant()
        tenant.parameters = dict(state='present' if is_present else 'absent')
        tenant._get_tenant = mock.MagicMock(return_value=dict())
        tenant._ensure_present = mock.MagicMock()
        tenant._ensure_absent = mock.MagicMock()
        tenant._execute()
        if is_present:
            tenant._ensure_present.assert_called_once_with(mock.ANY)
            tenant._ensure_absent.assert_not_called()
        else:
            tenant._ensure_absent.assert_called_once_with(mock.ANY)
            tenant._ensure_present.assert_not_called()

    def test_get_tenant_exists(self):
        expected_tenant_dict = dict(
            name='Example',
            display_name='Tenant for the Example Company Ltd',
            billing_id='123',
            company='Example Company Ltd',
            comment='Another comment',
            plan='Best',
            activation_status='Enabled'
        )
        tenant_obj_dict = copy.deepcopy(expected_tenant_dict)
        tenant_obj_dict['displayName'] = tenant_obj_dict.pop('display_name')
        tenant_obj_dict['externalPortalId'] = tenant_obj_dict.pop('billing_id')
        tenant_obj_dict['companyName'] = tenant_obj_dict.pop('company')
        tenant_obj_dict['activationStatus'] = tenant_obj_dict.pop('activation_status')

        tenant = ctera_portal_tenant.CteraPortalTenant()
        tenant.parameters = dict(name=expected_tenant_dict['name'])
        tenant._ctera_portal.portals.get = mock.MagicMock(return_value=munch.Munch(tenant_obj_dict))
        tenant._ctera_portal.get = mock.MagicMock(
            return_value=munch.Munch(dict(baseObjectRef=tenant_obj_dict['plan'], name=tenant_obj_dict['plan']))
        )
        self.assertDictEqual(expected_tenant_dict, tenant._get_tenant())

    def test__get_tenant_doesnt_exist(self):
        tenant = ctera_portal_tenant.CteraPortalTenant()
        tenant.parameters = dict(name='example')
        tenant._ctera_portal.portals.get = mock.MagicMock(side_effect=CTERAException(response=munch.Munch(code=404)))
        self.assertIsNone(tenant._get_tenant())

    def test_ensure_present(self):
        for is_present in [True, False]:
            self._test_ensure_present(is_present=is_present)

    @staticmethod
    def _test_ensure_present(is_present):
        tenant = ctera_portal_tenant.CteraPortalTenant()
        tenant._handle_create = mock.MagicMock()
        tenant._handle_modify = mock.MagicMock()
        tenant._ensure_present({'name': 'example'} if is_present else None)
        if is_present:
            tenant._handle_modify.assert_called_once_with(mock.ANY)
            tenant._handle_create.assert_not_called()
        else:
            tenant._handle_create.assert_called_once_with()
            tenant._handle_modify.assert_not_called()

    def test__handle_create(self):
        parameters = dict(
            name='Example',
            display_name='Tenant for the Example Company Ltd',
            billing_id='123',
            company='Example Company Ltd',
            comment='Another comment',
            plan='Best',
        )
        tenant = ctera_portal_tenant.CteraPortalTenant()
        tenant.parameters = parameters
        tenant._handle_create()
        tenant._ctera_portal.portals.add.assert_called_with(**parameters)

    def test__handle_modify(self):
        for is_deleted in [True, False]:
            for change_attributes in [True, False]:
                self._test__handle_modify(is_deleted=is_deleted, change_attributes=change_attributes)

    @staticmethod
    def _test__handle_modify(is_deleted=False, change_attributes=False):
        current_attributes = dict(
            name='Example',
            display_name='Tenant for the Example Company Ltd',
            billing_id='123',
            company='Example Company Ltd',
            comment='Another comment',
            plan='Best',
            activation_status='Disabled' if is_deleted else 'Enabled'
        )
        desired_attributes = copy.deepcopy(current_attributes)
        desired_attributes.pop('activation_status')
        if change_attributes:
            desired_attributes['billing_id'] = '456'
            desired_attributes['plan'] = 'Good'
        tenant = ctera_portal_tenant.CteraPortalTenant()
        tenant.parameters = desired_attributes
        tenant._ensure_present(current_attributes)
        if is_deleted:
            tenant._ctera_portal.portals.undelete.assert_called_with(desired_attributes['name'])
        if change_attributes:
            tenant._ctera_portal.portals.subscribe.assert_called_with(
                desired_attributes['name'],
                desired_attributes['plan']
            )

    def test_ensure_absent(self):
        for is_present in [True, False]:
            self._test_ensure_absent(is_present)

    @staticmethod
    def _test_ensure_absent(is_present):
        name = 'example'
        tenant = ctera_portal_tenant.CteraPortalTenant()
        tenant.parameters = dict(name=name)
        tenant._ensure_absent(tenant.parameters if is_present else None)
        if is_present:
            tenant._ctera_portal.portals.delete.assert_called_once_with(name)
        else:
            tenant._ctera_portal.portals.delete.assert_not_called()

    def test__get_plan_name(self):
        for exists in [True, False]:
            self._test__get_plan_name(exists)

    def _test__get_plan_name(self, exists):
        plan = {
            'name': 'Best',
            'baseObjectRef': '/objs/1234'
        }
        tenant = ctera_portal_tenant.CteraPortalTenant()
        tenant._ctera_portal.get = mock.MagicMock(return_value=munch.Munch(plan) if exists else None)
        plan_name = tenant._get_plan_name(plan['baseObjectRef'])
        if exists:
            self.assertEqual(plan['name'], plan_name)
        else:
            self.assertIsNone(plan_name)
