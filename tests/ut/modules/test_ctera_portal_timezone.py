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

import ansible_collections.ctera.ctera.plugins.modules.ctera_portal_timezone as ctera_portal_timezone
import tests.ut.mocks.ctera_portal_base_mock as ctera_portal_base_mock
from tests.ut.base import BaseTest


class TestCteraFilerTimezone(BaseTest):

    def setUp(self):
        super().setUp()
        ctera_portal_base_mock.mock_bases(self, ctera_portal_timezone.CteraPortalTimezone)

    def test_execute(self):
        for change_timezone in [True, False]:
            self._test_execute(change_timezone)

    def _test_execute(self, change_timezone):
        current_timezone = 'current'
        new_timezone = 'new'
        timezone = ctera_portal_timezone.CteraPortalTimezone()
        timezone.parameters = dict(timezone=new_timezone if change_timezone else current_timezone)
        timezone._ctera_portal.settings.global_settings.get_timezone.return_value = current_timezone
        timezone._execute()
        if change_timezone:
            timezone._ctera_portal.settings.global_settings.set_timezone.assert_called_once_with(new_timezone)
            self.assertTrue(timezone.ansible_return_value.param.changed)
            self.assertEqual(timezone.ansible_return_value.param.msg, 'Changed timezone')
            self.assertEqual(timezone.ansible_return_value.param.previous_timezone, current_timezone)
            self.assertEqual(timezone.ansible_return_value.param.current_timezone, new_timezone)
        else:
            timezone._ctera_portal.settings.global_settings.set_timezone.assert_not_called()
            self.assertFalse(hasattr(timezone.ansible_return_value.param, 'changed'))
            self.assertEqual(timezone.ansible_return_value.param.msg, 'No update required to the current timezone')
            self.assertEqual(timezone.ansible_return_value.param.current_timezone, current_timezone)
