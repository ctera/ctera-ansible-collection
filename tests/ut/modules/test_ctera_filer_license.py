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

import ansible_collections.ctera.ctera.plugins.modules.ctera_filer_license as ctera_filer_license
import tests.ut.mocks.ctera_filer_base_mock as ctera_filer_base_mock
from tests.ut.base import BaseTest


class TestCteraFilerLicense(BaseTest):

    def setUp(self):
        super().setUp()
        ctera_filer_base_mock.mock_bases(self, ctera_filer_license.CteraFilerLicense)

    def test_execute(self):
        for change_license in [True, False]:
            self._test_execute(change_license)

    def _test_execute(self, change_license):
        current_license = 'EV16'
        new_license = 'EV32'
        ctera_license = ctera_filer_license.CteraFilerLicense()
        ctera_license.parameters = dict(license=new_license if change_license else current_license)
        ctera_license._ctera_filer.licenses.get.return_value = current_license
        ctera_license._execute()
        if change_license:
            ctera_license._ctera_filer.licenses.apply.assert_called_once_with(new_license)
            self.assertTrue(ctera_license.ansible_return_value.param.changed)
            self.assertEqual(ctera_license.ansible_return_value.param.msg, 'License applied')
        else:
            ctera_license._ctera_filer.licenses.apply.assert_not_called()
            self.assertFalse(hasattr(ctera_license.ansible_return_value.param, 'changed'))
            self.assertTrue(ctera_license.ansible_return_value.param.skipped)
            self.assertEqual(ctera_license.ansible_return_value.param.msg, 'License has not changed')
        self.assertEqual(ctera_license.ansible_return_value.param.license, ctera_license.parameters['license'])
