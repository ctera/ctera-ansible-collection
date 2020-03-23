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

import ansible_collections.ctera.ctera.plugins.modules.ctera_filer_device_reboot as ctera_filer_device_reboot
import tests.ut.mocks.ctera_filer_base_mock as ctera_filer_base_mock
from tests.ut.base import BaseTest


class TestCteraFilerDeviceReboot(BaseTest):

    def setUp(self):
        super().setUp()
        ctera_filer_base_mock.mock_bases(self, ctera_filer_device_reboot.CteraFilerDeviceReboot)

    def test__execute(self):
        for wait in [True, False]:
            self._test__execute(wait)

    def _test__execute(self, wait):
        device_reboot = ctera_filer_device_reboot.CteraFilerDeviceReboot()
        device_reboot.parameters = dict(wait=wait)
        device_reboot._execute()
        device_reboot._ctera_filer.power.reboot.assert_called_once_with(wait)
        self.assertEqual(
            device_reboot.ansible_return_value.param.msg,
            'Filer is up and running' if wait else 'Rebooting device'
        )
