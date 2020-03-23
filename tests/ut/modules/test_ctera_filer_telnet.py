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

import ansible_collections.ctera.ctera.plugins.modules.ctera_filer_telnet as ctera_filer_telnet
import tests.ut.mocks.ctera_filer_base_mock as ctera_filer_base_mock
from tests.ut.base import BaseTest


class TestCteraFilerTelnet(BaseTest):

    def setUp(self):
        super().setUp()
        ctera_filer_base_mock.mock_bases(self, ctera_filer_telnet.CteraFilerTelnet)

    def test_execute(self):
        for enabled in [True, False]:
            self._test_execute(enabled)

    def _test_execute(self, enabled):
        telnet = ctera_filer_telnet.CteraFilerTelnet()
        telnet.parameters = dict(enabled=enabled, code='code')
        telnet._execute()
        if enabled:
            telnet._ctera_filer.telnet.enable.assert_called_once_with('code')
            telnet._ctera_filer.telnet.disable.assert_not_called()
        else:
            telnet._ctera_filer.telnet.disable.assert_called_once_with()
            telnet._ctera_filer.telnet.enable.assert_not_called()
        self.assertTrue(telnet.ansible_return_value.param.changed)
