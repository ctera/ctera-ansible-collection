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

import ansible_collections.ctera.ctera.plugins.modules.ctera_filer_first_user as ctera_filer_first_user
import tests.ut.mocks.ctera_filer_base_mock as ctera_filer_base_mock
from tests.ut.base import BaseTest


class TestCteraFilerFirstUser(BaseTest):

    def setUp(self):
        super().setUp()
        ctera_filer_base_mock.mock_bases(self, ctera_filer_first_user.CteraFilerFirstUser)

    def test__execute(self):
        for is_first_login in [True, False]:
            for with_email in [True, False]:
                self._test__execute(is_first_login, with_email)

    def _test__execute(self, is_first_login, with_email):
        first_user = ctera_filer_first_user.CteraFilerFirstUser()
        username = 'admin'
        password = 'password'
        email = 'admin@example.com'
        first_user.parameters = dict(filer_user=username, filer_password=password)
        if with_email:
            first_user.parameters['email'] = email
        first_user._ctera_filer.get = mock.MagicMock(return_value=munch.Munch(isfirstlogin=is_first_login))
        first_user._execute()
        if is_first_login:
            first_user._ctera_filer.users.add_first_user.assert_called_once_with(username, password, email=email if with_email else '')
            self.assertEqual(first_user.ansible_return_value.param.msg, 'User created')
            self.assertTrue(first_user.ansible_return_value.param.changed)
        else:
            self.assertEqual(first_user.ansible_return_value.param.msg, 'First user was already created')
        self.assertEqual(first_user.ansible_return_value.param.user, username)
