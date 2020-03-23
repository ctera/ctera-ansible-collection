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

import ansible_collections.ctera.ctera.plugins.modules.ctera_filer_cloud_cache as ctera_filer_cloud_cache
import tests.ut.mocks.ctera_filer_base_mock as ctera_filer_base_mock
from tests.ut.base import BaseTest


class TestCteraFilerCloudCache(BaseTest):

    def setUp(self):
        super().setUp()
        ctera_filer_base_mock.mock_bases(self, ctera_filer_cloud_cache.CteraFilerCloudSync)

    def test_not_connected(self):
        for desired in [True, False]:
            self._test_not_connected(desired)

    def _test_not_connected(self, desired):
        cloud_cache = ctera_filer_cloud_cache.CteraFilerCloudSync()
        cloud_cache.parameters = dict(enabled=desired)
        cloud_cache._ctera_filer.services.connected.return_value = False
        cloud_cache.run()
        self.assertEqual(cloud_cache.ansible_return_value.param.msg, 'Filer is not connected to Cloud Services')
        if desired:
            self.assertTrue(cloud_cache.ansible_return_value.has_failed())
        else:
            self.assertTrue(cloud_cache.ansible_return_value.param.skipped)

    def test__execute(self):
        for current in [True, False]:
            for desired in [True, False]:
                self._test__execute(current, desired)

    @staticmethod
    def _test__execute(current, desired):
        cloud_cache = ctera_filer_cloud_cache.CteraFilerCloudSync()
        cloud_cache._ctera_filer.services.connected.return_value = True
        cloud_cache._ctera_filer.cache.is_enabled.return_value = current
        cloud_cache.parameters = dict(enabled=desired)
        cloud_cache._ensure_cache_enabled = mock.MagicMock()
        cloud_cache._ensure_cache_disabled = mock.MagicMock()
        cloud_cache._execute()
        if desired:
            cloud_cache._ensure_cache_enabled.assert_called_once_with(current)
            cloud_cache._ensure_cache_disabled.assert_not_called()
        else:
            cloud_cache._ensure_cache_enabled.assert_not_called()
            cloud_cache._ensure_cache_disabled.assert_called_once_with(current)

    def test__ensure_cache_enabled(self):
        for is_cache_enabled in [True, False]:
            for force_eviction in [True, False]:
                for current_sync in [True, False]:
                    for desired_sync in [True, False]:
                        self._test__ensure_cache_enabled(is_cache_enabled, force_eviction, current_sync, desired_sync)

    def _test__ensure_cache_enabled(self, is_cache_enabled, force_eviction, current_sync, desired_sync):
        expected_changed = False
        cloud_cache = ctera_filer_cloud_cache.CteraFilerCloudSync()
        cloud_cache.parameters = dict(force_eviction=force_eviction, sync_enabled=desired_sync)
        cloud_cache._ctera_filer.sync.is_enabled.return_value = current_sync
        cloud_cache._ensure_sync_enabled = mock.MagicMock()
        cloud_cache._ensure_sync_disabled = mock.MagicMock()
        cloud_cache._ensure_cache_enabled(is_cache_enabled)
        if is_cache_enabled:
            cloud_cache._ctera_filer.cache.enable.assert_not_called()
        else:
            expected_changed = True
            cloud_cache._ctera_filer.cache.enable.assert_called_once_with()
        if force_eviction:
            expected_changed = True
            cloud_cache._ctera_filer.cache.force_eviction.assert_called_once_with()
        else:
            cloud_cache._ctera_filer.cache.force_eviction.assert_not_called()
        if desired_sync:
            cloud_cache._ensure_sync_enabled.assert_called_once_with(current_sync, mock.ANY)
        else:
            cloud_cache._ensure_sync_disabled.assert_called_once_with(current_sync, mock.ANY)
        if expected_changed:
            self.assertTrue(cloud_cache.ansible_return_value.param.changed)
        else:
            self.assertFalse(hasattr(cloud_cache.ansible_return_value.param, 'changed'))

    def test__ensure_cache_disabled(self):
        for is_cache_enabled in [True, False]:
            self._test__ensure_cache_disabled(is_cache_enabled)

    def _test__ensure_cache_disabled(self, is_cache_enabled):
        cloud_cache = ctera_filer_cloud_cache.CteraFilerCloudSync()
        cloud_cache._ensure_cache_disabled(is_cache_enabled)
        if is_cache_enabled:
            cloud_cache._ctera_filer.cache.disable.assert_called_once_with()
            self.assertTrue(cloud_cache.ansible_return_value.param.changed)
            self.assertEqual(cloud_cache.ansible_return_value.param.msg, 'Cloud cache was disabled')
        else:
            cloud_cache._ctera_filer.cache.disable.assert_not_called()
            self.assertTrue(cloud_cache.ansible_return_value.param.skipped)
            self.assertEqual(cloud_cache.ansible_return_value.param.msg, 'Cloud cache is already disabled')

    def test__ensure_sync_enabled(self):
        for is_sync_enabled in [True, False]:
            for volume_exists in [True, False]:
                for refresh_folders in [True, False]:
                    self._test__ensure_sync_enabled(is_sync_enabled, volume_exists, refresh_folders)

    def _test__ensure_sync_enabled(self, is_sync_enabled, volume_exists, refresh_folders):
        expected_messages = dict(skipped=[], changed=[])
        messages = dict(skipped=[], changed=[])
        cloud_cache = ctera_filer_cloud_cache.CteraFilerCloudSync()
        cloud_cache.parameters = dict(refresh_folders=refresh_folders)
        cloud_cache._ctera_filer.volumes.get.return_value = [{}] if volume_exists else []
        cloud_cache._ensure_sync_enabled(is_sync_enabled, messages)
        if is_sync_enabled:
            cloud_cache._ctera_filer.sync.unsuspend.assert_not_called()
            expected_messages['skipped'].append('Cloud sync was already enabled')
        else:
            if volume_exists:
                expected_messages['changed'].append('Cloud sync was enabled')
                cloud_cache._ctera_filer.sync.unsuspend.assert_called_once_with()
            else:
                cloud_cache._ctera_filer.sync.unsuspend.assert_not_called()
                expected_messages['skipped'].append('No volumes defined - cannot enabled sync')
        if refresh_folders:
            if is_sync_enabled or volume_exists:
                cloud_cache._ctera_filer.sync.refresh.assert_called_once_with()
                expected_messages['changed'].append('Started refreshing cloud folders')
            else:
                cloud_cache._ctera_filer.sync.refresh.assert_not_called()
        else:
            cloud_cache._ctera_filer.sync.refresh.assert_not_called()
        self.assertDictEqual(expected_messages, messages)

    def test__ensure_sync_disabled(self):
        for is_sync_enabled in [True, False]:
            self._test__ensure_sync_disabled(is_sync_enabled)

    def _test__ensure_sync_disabled(self, is_sync_enabled):
        messages = dict(skipped=[], changed=[])
        cloud_cache = ctera_filer_cloud_cache.CteraFilerCloudSync()
        cloud_cache._ensure_sync_disabled(is_sync_enabled, messages)
        if is_sync_enabled:
            cloud_cache._ctera_filer.sync.suspend.assert_called_once_with()
            self.assertEqual(messages['changed'], ['Cloud sync was disabled'])
        else:
            cloud_cache._ctera_filer.sync.suspend.assert_not_called()
            self.assertEqual(messages['skipped'], ['Cloud sync was already disabled'])
