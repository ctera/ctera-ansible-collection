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

import ansible_collections.ctera.ctera.plugins.modules.ctera_filer_array as ctera_filer_array
import tests.ut.mocks.ctera_filer_base_mock as ctera_filer_base_mock
from tests.ut.base import BaseTest


class TestCteraFilerArray(BaseTest):

    def setUp(self):
        super().setUp()
        ctera_filer_base_mock.mock_bases(self, ctera_filer_array.CteraFilerArray)

    def test__execute(self):
        for is_present in [True, False]:
            self._test__execute(is_present)

    @staticmethod
    def _test__execute(is_present):
        array = ctera_filer_array.CteraFilerArray()
        array.parameters = dict(state='present' if is_present else 'absent')
        array._get_array = mock.MagicMock(return_value=dict())
        array._ensure_present = mock.MagicMock()
        array._ensure_absent = mock.MagicMock()
        array._execute()
        if is_present:
            array._ensure_present.assert_called_once_with(mock.ANY)
            array._ensure_absent.assert_not_called()
        else:
            array._ensure_absent.assert_called_once_with(mock.ANY)
            array._ensure_present.assert_not_called()

    def test_get_array_exists(self):
        expected_array_dict = dict(
            array_name='array',
            level='linear',
            members=['VIRT2', 'VIRT3']
        )
        array_object_dict = copy.deepcopy(expected_array_dict)
        array_object_dict['_classname'] = 'className'
        array = ctera_filer_array.CteraFilerArray()
        array.parameters = dict(array_name='array')
        array._ctera_filer.array.get = mock.MagicMock(return_value=munch.Munch(array_object_dict))
        self.assertDictEqual(expected_array_dict, array._get_array())

    def test__get_array_doesnt_exist(self):
        array = ctera_filer_array.CteraFilerArray()
        array.parameters = dict(array_name='array')
        array._ctera_filer.array.get = mock.MagicMock(side_effect=CTERAException(response=munch.Munch(code=404)))
        self.assertDictEqual(array._get_array(), {})

    def test__get_array_failed(self):
        array = ctera_filer_array.CteraFilerArray()
        array.parameters = dict(array_name='array')
        array._ctera_filer.array.get = mock.MagicMock(side_effect=CTERAException(response=munch.Munch(code=401)))
        self.assertRaises(CTERAException, array._get_array)

    def test_ensure_present(self):
        for is_present in [True, False]:
            for change_attributes in [True, False]:
                self._test_ensure_present(is_present, change_attributes)

    @staticmethod
    def _test_ensure_present(is_present, change_attributes):
        current_attributes = dict(
            array_name='array',
            level='linear',
            members=['VIRT2', 'VIRT3']
        )
        array = ctera_filer_array.CteraFilerArray()
        array.parameters = current_attributes
        array._ensure_present(current_attributes if is_present else None)
        if is_present:
            array._ctera_filer.array.add.assert_not_called()
        else:
            array._ctera_filer.array.add.assert_called_once_with(**current_attributes)

    def test_ensure_absent(self):
        for is_present in [True, False]:
            self._test_ensure_absent(is_present)

    @staticmethod
    def _test_ensure_absent(is_present):
        name = 'array'
        array = ctera_filer_array.CteraFilerArray()
        array.parameters = dict(array_name=name)
        array._ensure_absent(array.parameters if is_present else None)
        if is_present:
            array._ctera_filer.array.delete.assert_called_once_with(name)
        else:
            array._ctera_filer.array.delete.assert_not_called()
