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

try:
    from cterasdk import CTERAException
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common

import ansible_collections.ctera.ctera.plugins.modules.ctera_filer_volume as ctera_filer_volume
import tests.ut.mocks.ctera_filer_base_mock as ctera_filer_base_mock
from tests.ut.base import BaseTest


class TestCteraFilerVolume(BaseTest):

    def setUp(self):
        super().setUp()
        ctera_filer_base_mock.mock_bases(self, ctera_filer_volume.CteraFilerVolume)

    def test__execute(self):
        for is_present in [True, False]:
            self._test__execute(is_present)

    @staticmethod
    def _test__execute(is_present):
        volume = ctera_filer_volume.CteraFilerVolume()
        volume.parameters = dict(state='present' if is_present else 'absent')
        volume._get_volume = mock.MagicMock(return_value=dict())
        volume._ensure_present = mock.MagicMock()
        volume._ensure_absent = mock.MagicMock()
        volume._execute()
        if is_present:
            volume._ensure_present.assert_called_once_with(mock.ANY)
            volume._ensure_absent.assert_not_called()
        else:
            volume._ensure_absent.assert_called_once_with(mock.ANY)
            volume._ensure_present.assert_not_called()

    def test_get_volume_exists(self):
        expected_volume_dict = dict(
            name='volume_name',
            size=1024,
            filesystem='xfs',
            device='/dev/sd1',
            passphrase='passphrase'
        )
        volume_object_dict = copy.deepcopy(expected_volume_dict)
        volume_object_dict['_classname'] = 'className'
        volume = ctera_filer_volume.CteraFilerVolume()
        volume.parameters = dict(name='volume_name')
        volume._ctera_filer.volumes.get = mock.MagicMock(return_value=munch.Munch(volume_object_dict))
        self.assertDictEqual(expected_volume_dict, volume._get_volume())

    def test__get_volume_doesnt_exist(self):
        volume = ctera_filer_volume.CteraFilerVolume()
        volume.parameters = dict(name='volume_name')
        volume._ctera_filer.volumes.get = mock.MagicMock(side_effect=CTERAException(response=munch.Munch(code=404)))
        self.assertDictEqual(volume._get_volume(), {})

    def test__get_volume_failed(self):
        volume = ctera_filer_volume.CteraFilerVolume()
        volume.parameters = dict(name='volume_name')
        volume._ctera_filer.volumes.get = mock.MagicMock(side_effect=CTERAException(response=munch.Munch(code=401)))
        self.assertRaises(CTERAException, volume._get_volume)

    def test_ensure_present(self):
        for is_present in [True, False]:
            for change_attributes in [True, False]:
                self._test_ensure_present(is_present, change_attributes)

    @staticmethod
    def _test_ensure_present(is_present, change_attributes):
        current_attributes = dict(
            name='volume_name',
            size=1024,
            filesystem='xfs',
            device='/dev/sd1',
            passphrase='passphrase'
        )
        desired_attributes = copy.deepcopy(current_attributes)
        if change_attributes:
            desired_attributes['size'] = 2048
        volume = ctera_filer_volume.CteraFilerVolume()
        volume.parameters = desired_attributes
        volume._ensure_present(current_attributes if is_present else None)
        if is_present:
            if change_attributes:
                volume._ctera_filer.volumes.modify.assert_called_with(desired_attributes['name'], size=desired_attributes['size'])
            else:
                volume._ctera_filer.volumes.modify.assert_not_called()
        else:
            volume._ctera_filer.volumes.add.assert_called_with(**desired_attributes)

    @staticmethod
    def test_modify_not_size():
        current_attributes = dict(
            name='volume_name',
            size=1024,
            filesystem='xfs',
            device='/dev/sd1',
            passphrase='passphrase'
        )
        desired_attributes = copy.deepcopy(current_attributes)
        desired_attributes['filesystem'] = 'ext4'
        volume = ctera_filer_volume.CteraFilerVolume()
        volume.parameters = desired_attributes
        volume._ensure_present(current_attributes)
        volume._ctera_filer.volumes.modify.assert_not_called()

    def test_ensure_absent(self):
        for is_present in [True, False]:
            self._test_ensure_absent(is_present)

    @staticmethod
    def _test_ensure_absent(is_present):
        name = 'volume_name'
        volume = ctera_filer_volume.CteraFilerVolume()
        volume.parameters = dict(name=name)
        volume._ensure_absent(volume.parameters if is_present else None)
        if is_present:
            volume._ctera_filer.volumes.delete.assert_called_once_with(name)
        else:
            volume._ctera_filer.volumes.delete.assert_not_called()
