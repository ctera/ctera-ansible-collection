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

import ansible_collections.ctera.ctera.plugins.modules.ctera_filer_backup as ctera_filer_backup
import tests.ut.mocks.ctera_filer_base_mock as ctera_filer_base_mock
from tests.ut.base import BaseTest


class TestCteraFilerBackup(BaseTest):

    def setUp(self):
        super().setUp()
        ctera_filer_base_mock.mock_bases(self, ctera_filer_backup.CteraFilerBackup)

    def test_execute(self):
        for is_configured in [True, False]:
            self._test_execute(is_configured)

    def _test_execute(self, is_configured):
        expected_passphrase = 'passphrase'
        backup = ctera_filer_backup.CteraFilerBackup()
        backup.parameters = dict(passphrase=expected_passphrase)
        backup._ctera_filer.backup.is_configured.return_value = is_configured  # pylint: disable=protected-access
        backup.run()
        if is_configured:
            backup._ctera_filer.backup.configure.assert_not_called()  # pylint: disable=protected-access
            self.assertFalse(hasattr(backup.ansible_return_value.param, 'changed'))
            self.assertEqual(backup.ansible_return_value.param.msg, 'Cloud Backup is already configured')
        else:
            backup._ctera_filer.backup.configure.assert_called_once_with(expected_passphrase)  # pylint: disable=protected-access
            self.assertTrue(backup.ansible_return_value.param.changed)
            self.assertEqual(backup.ansible_return_value.param.msg, 'Configured cloud backup')
