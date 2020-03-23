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

import ansible_collections.ctera.ctera.plugins.module_utils.ctera_filer_share_config_base as ctera_filer_share_config_base
import tests.ut.mocks.ctera_filer_base_mock as ctera_filer_base_mock
from tests.ut.base import BaseTest

class ShareConfigMock(ctera_filer_share_config_base.CteraFilerShareConfigBase):
    def __init__(self):
        super().__init__(dict())
        self.called__to_config_dict = False

    @property
    def _share_type(self):
        return "MOCK"

    @property
    def _manager(self):
        return self._ctera_filer.share_mock

    def _to_config_dict(self, config):
        self.called__to_config_dict = True
        return config.__dict__


class TestCteraFilerAsyncIO(BaseTest):

    def setUp(self):
        super().setUp()
        ctera_filer_base_mock.mock_bases(self, ctera_filer_share_config_base.CteraFilerShareConfigBase)

    def test__execute(self):
        for is_enabled in [True, False]:
            self._test__execute(is_enabled)

    @staticmethod
    def _test__execute(is_enabled):
        share_config = ShareConfigMock()
        share_config.parameters = dict(enabled=is_enabled)
        share_config._ensure_enabled = mock.MagicMock()
        share_config._ensure_disabled = mock.MagicMock()
        share_config._get_current_config = mock.MagicMock()
        share_config._execute()
        share_config._get_current_config.assert_called()
        if is_enabled:
            share_config._ensure_enabled.assert_called_once_with(mock.ANY)
            share_config._ensure_disabled.assert_not_called()
        else:
            share_config._ensure_disabled.assert_called_once_with(mock.ANY)
            share_config._ensure_enabled.assert_not_called()

    def test__get_current_config(self):
        expected_dict = dict(name='name')
        share_config = ShareConfigMock()
        share_config._ctera_filer.share_mock.get_configuration = mock.MagicMock(return_value=munch.Munch(expected_dict))
        self.assertDictEqual(expected_dict, share_config._get_current_config())
        self.assertTrue(share_config.called__to_config_dict)

    def test__ensure_enabled(self):
        for is_enabled in [True, False]:
            for change_attributes in [True, False]:
                self._test__ensure_enabled(is_enabled, change_attributes)

    @staticmethod
    def _test__ensure_enabled(is_enabled, change_attributes):
        current_attributes = dict(
            mode='enabled' if is_enabled else 'disabled',
            name='name',
            size=1024,
        )
        after_enable_attributes = copy.deepcopy(current_attributes)
        after_enable_attributes['mode'] = 'enabled'
        desired_attributes = copy.deepcopy(after_enable_attributes)
        if change_attributes:
            desired_attributes['size'] = 2048
        share_config = ShareConfigMock()
        share_config._get_current_config = mock.MagicMock(return_value=after_enable_attributes)
        share_config.parameters = desired_attributes

        share_config._ensure_enabled(current_attributes)
        if is_enabled:
            share_config._ctera_filer.share_mock.enable.assert_not_called()
        else:
            share_config._ctera_filer.share_mock.enable.assert_called_once_with()
        if change_attributes:
            share_config._ctera_filer.share_mock.modify.assert_called_once_with(size=2048)
        else:
            share_config._ctera_filer.share_mock.modify.assert_not_called()

    def test__ensure_disabled(self):
        for is_enabled in [True, False]:
            self._test__ensure_disabled(is_enabled)

    @staticmethod
    def _test__ensure_disabled(is_enabled):
        share_config = ShareConfigMock()
        share_config._ensure_disabled(dict(mode='enabled' if is_enabled else 'disabled'))
        if is_enabled:
            share_config._ctera_filer.share_mock.disable.assert_called_once_with()
        else:
            share_config._ctera_filer.share_mock.disable.assert_not_called()
