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

import ansible_collections.ctera.ctera.plugins.modules.ctera_filer_hostname as ctera_filer_hostname
import tests.ut.mocks.ctera_filer_base_mock as ctera_filer_base_mock
from tests.ut.base import BaseTest


class TestCteraFilerHostname(BaseTest):

    def setUp(self):
        super().setUp()
        ctera_filer_base_mock.mock_bases(self, ctera_filer_hostname.CteraFilerHostname)

    def test_execute(self):
        for change_name in [True, False]:
            self._test_execute(change_name)

    def _test_execute(self, change_name):
        current_name = 'current'
        new_name = 'new'
        hostname = ctera_filer_hostname.CteraFilerHostname()
        hostname.parameters = dict(hostname=new_name if change_name else current_name)
        hostname._ctera_filer.config.get_hostname.return_value = current_name
        hostname._execute()
        if change_name:
            hostname._ctera_filer.config.set_hostname.assert_called_once_with(new_name)
            self.assertTrue(hostname.ansible_return_value.param.changed)
            self.assertEqual(hostname.ansible_return_value.param.msg, 'Changed hostname')
            self.assertEqual(hostname.ansible_return_value.param.previous_hostname, current_name)
            self.assertEqual(hostname.ansible_return_value.param.current_hostname, new_name)
        else:
            hostname._ctera_filer.config.set_hostname.assert_not_called()
            self.assertFalse(hasattr(hostname.ansible_return_value.param, 'changed'))
            self.assertEqual(hostname.ansible_return_value.param.msg, 'No update required to the current hostname')
            self.assertEqual(hostname.ansible_return_value.param.current_hostname, current_name)
