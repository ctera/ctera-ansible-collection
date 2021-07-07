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

import ansible_collections.ctera.ctera.plugins.modules.ctera_filer_domain_controllers as ctera_filer_domain_controllers
import tests.ut.mocks.ctera_filer_base_mock as ctera_filer_base_mock
from tests.ut.base import BaseTest


class TestCteraFilerDomainControllers(BaseTest):

    def setUp(self):
        super().setUp()
        self._current_domain_controllers = ['192.168.0.1']
        self._new_domain_controllers = ['172.0.52.1', '192.168.50.100''*']
        ctera_filer_base_mock.mock_bases(self, ctera_filer_domain_controllers.CteraFilerDomainControllers)

    def test_ensure_present(self):
        self._test_ensure_present(True, self._new_domain_controllers)
        self._test_ensure_present(False, self._current_domain_controllers)

    def _test_ensure_present(self, changed, domain_controllers):
        dc = ctera_filer_domain_controllers.CteraFilerDomainControllers()
        dc.parameters = dict(
            state='present',
            domain_controllers=domain_controllers
        )
        dc._ctera_filer.directoryservice.get_static_domain_controller = mock.MagicMock(return_value=' '.join(self._current_domain_controllers))
        dc._ctera_filer.directoryservice.set_static_domain_controller = mock.MagicMock()
        dc._execute()
        dc._ctera_filer.directoryservice.get_static_domain_controller.assert_called_once()
        if changed:
            dc._ctera_filer.directoryservice.set_static_domain_controller.assert_called_once_with(' '.join(domain_controllers))
            self.assertTrue(dc.ansible_return_value.param.changed)
        else:
            dc._ctera_filer.directoryservice.set_static_domain_controller.assert_not_called()
            self.assertTrue(dc.ansible_return_value.param.skipped)

    def test_ensure_absent(self):
        self._test_ensure_absent(True, self._current_domain_controllers)
        self._test_ensure_absent(False, None)

    def _test_ensure_absent(self, changed, domain_controllers):
        dc = ctera_filer_domain_controllers.CteraFilerDomainControllers()
        dc.parameters = dict(
            state='absent'
        )
        dc._ctera_filer.directoryservice.get_static_domain_controller = mock.MagicMock(return_value=domain_controllers)
        dc._ctera_filer.directoryservice.remove_static_domain_controller = mock.MagicMock()
        dc._execute()
        if changed:
            dc._ctera_filer.directoryservice.remove_static_domain_controller.assert_called_once()
            self.assertTrue(dc.ansible_return_value.param.changed)
        else:
            dc._ctera_filer.directoryservice.remove_static_domain_controller.assert_not_called()
            self.assertTrue(dc.ansible_return_value.param.skipped)
