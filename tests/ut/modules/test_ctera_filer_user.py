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
    from cterasdk import CTERAException
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common

import ansible_collections.ctera.ctera.plugins.modules.ctera_filer_user as ctera_filer_user
import tests.ut.mocks.ctera_filer_base_mock as ctera_filer_base_mock
from tests.ut.base import BaseTest


class TestCteraFilerUser(BaseTest):

    def setUp(self):
        super().setUp()
        ctera_filer_base_mock.mock_bases(self, ctera_filer_user.CteraFilerUser)

    def test__execute(self):
        for is_present in [True, False]:
            self._test__execute(is_present)

    @staticmethod
    def _test__execute(is_present):
        user = ctera_filer_user.CteraFilerUser()
        user.parameters = dict(state='present' if is_present else 'absent')
        user._get_user = mock.MagicMock(return_value=dict())
        user._ensure_present = mock.MagicMock()
        user._ensure_absent = mock.MagicMock()
        user._execute()
        if is_present:
            user._ensure_present.assert_called_once_with(mock.ANY)
            user._ensure_absent.assert_not_called()
        else:
            user._ensure_absent.assert_called_once_with(mock.ANY)
            user._ensure_present.assert_not_called()

    def test_get_user_exists(self):
        expected_user_dict = dict(
            username='admin',
            password='password',
            full_name='Admin',
            email='admin@example.com',
            uid='uid'
        )
        user_object_dict = copy.deepcopy(expected_user_dict)
        user_object_dict['fullName'] = user_object_dict.pop('full_name')
        user = ctera_filer_user.CteraFilerUser()
        user.parameters = dict(username='admin')
        user._ctera_filer.users.get = mock.MagicMock(return_value=munch.Munch(user_object_dict))
        self.assertDictEqual(expected_user_dict, user._get_user())

    def test__get_user_doesnt_exist(self):
        user = ctera_filer_user.CteraFilerUser()
        user.parameters = dict(username='admin')
        user._ctera_filer.users.get = mock.MagicMock(side_effect=CTERAException(response=munch.Munch(code=404)))
        self.assertIsNone(user._get_user())

    def test__get_user_failed(self):
        user = ctera_filer_user.CteraFilerUser()
        user.parameters = dict(username='admin')
        user._ctera_filer.users.get = mock.MagicMock(side_effect=CTERAException(response=munch.Munch(code=401)))
        self.assertRaises(CTERAException, user._get_user)

    def test_ensure_present(self):
        for is_present in [True, False]:
            for change_attributes in [True, False]:
                self._test_ensure_present(is_present, change_attributes)

    @staticmethod
    def _test_ensure_present(is_present, change_attributes):
        current_attributes = dict(
            username='admin',
            password='password',
            full_name='Admin',
            email='admin@example.com',
            uid='uid'
        )
        desired_attributes = copy.deepcopy(current_attributes)
        if change_attributes:
            desired_attributes['full_name'] = 'Administrator'
        user = ctera_filer_user.CteraFilerUser()
        user.parameters = desired_attributes
        user._ensure_present(current_attributes if is_present else None)
        if is_present:
            if change_attributes:
                user._ctera_filer.users.modify.assert_called_with(desired_attributes['username'], full_name=desired_attributes['full_name'])
            else:
                user._ctera_filer.users.modify.assert_not_called()
        else:
            user._ctera_filer.users.add.assert_called_with(**desired_attributes)

    def test_create_no_password(self):
        user = ctera_filer_user.CteraFilerUser()
        user.parameters = dict(
            username='admin',
            full_name='Admin',
            email='admin@example.com',
            uid='uid'
        )
        self.assertRaises(CTERAException, user._ensure_present, None)

    def test_ensure_absent(self):
        for is_present in [True, False]:
            self._test_ensure_absent(is_present)

    @staticmethod
    def _test_ensure_absent(is_present):
        username = 'admin'
        user = ctera_filer_user.CteraFilerUser()
        user.parameters = dict(username=username)
        user._ensure_absent(user.parameters if is_present else None)
        if is_present:
            user._ctera_filer.users.delete.assert_called_once_with(username)
        else:
            user._ctera_filer.users.delete.assert_not_called()
