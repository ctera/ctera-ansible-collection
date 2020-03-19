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

import unittest
import unittest.mock as mock

try:
    from cterasdk import CTERAException
except ImportError:  # pragma: no cover
    pass

import ansible_collections.ctera.ctera.plugins.module_utils.ctera_common as ctera_common


class TestCteraCommon(unittest.TestCase):  #pylint: disable=too-many-public-methods

    def test_ansible_return_value(self):
        ansible_return_value = ctera_common.AnsibleReturnValue()
        self.assertFalse(ansible_return_value.has_failed())

        ansible_return_value.changed()
        self.assertTrue(ansible_return_value.param.changed)

        ansible_return_value.failed()
        self.assertTrue(ansible_return_value.has_failed())

        ansible_return_value.skipped()
        self.assertTrue(ansible_return_value.param.skipped)

        msg = "test message"
        ansible_return_value.msg(msg)
        self.assertEqual(msg, ansible_return_value.param.msg)

        rc_value = 0
        ansible_return_value.rc(rc_value)
        self.assertEqual(rc_value, ansible_return_value.param.rc)

        first_warning = "First Warning"
        ansible_return_value.warning(first_warning)
        self.assertEqual([first_warning], ansible_return_value.param.warnings)
        second_warning = "Second Warning"
        ansible_return_value.warning(second_warning)
        self.assertEqual([first_warning, second_warning], ansible_return_value.param.warnings)

        ansible_return_value = ctera_common.AnsibleReturnValue()
        put_values = dict(boolean=True, string='string', integer=3, none=None)
        ansible_return_value.put(**put_values)
        put_values['failed'] = False
        self.assertDictEqual(put_values, ansible_return_value.as_dict())

    def test_get_parameters(self):
        ansible_parameters = dict(boolean=True, string='string', integer=3, none=None)
        parameters = ctera_common.get_parameters(ansible_parameters)
        expected_parameters = {k: v for k, v in ansible_parameters.items() if v is not None}
        self.assertDictEqual(expected_parameters, parameters)

    def test_filter_parameters(self):
        all_parameters = dict(first='a', second='b')
        filter_keys = ['first']
        filtered_parameters = ctera_common.filter_parameters(all_parameters, filter_keys)
        self.assertDictEqual(dict(first='a'), filtered_parameters)

    def test_cmp_int(self):
        self.assertEqual(ctera_common.cmp(1, 1), 0)
        self.assertNotEqual(ctera_common.cmp(1, 2), 0)

    def test_cmp_str(self):
        self.assertEqual(ctera_common.cmp("hello", "hello"), 0)
        self.assertNotEqual(ctera_common.cmp("hello", "world"), 0)

    def test_cmp_list(self):
        self.assertEqual(ctera_common.cmp(["hello"], ["hello"]), 0)
        self.assertNotEqual(ctera_common.cmp(["hello"], ["world"]), 0)

    def test_cmp_mix(self):
        self.assertNotEqual(ctera_common.cmp(1, "hello"), 0)
        self.assertNotEqual(ctera_common.cmp("hello", ["hello"]), 0)

    def test_cmp_none(self):
        self.assertNotEqual(ctera_common.cmp(None, 1), 0)

    def test_compare_lists_equal(self):
        current = ["hello", "world"]
        self.assertListEqual(ctera_common.compare_lists(current, current, False), [])

    def test_compare_lists_equal_reorder(self):
        current = ["hello", "world"]
        desired = ["world", "hello"]
        self.assertListEqual(ctera_common.compare_lists(current, desired, False), [])

    def test_compare_lists_get_desired(self):
        current = ["hello", "world"]
        desired = ["hello", "bar"]
        self.assertListEqual(ctera_common.compare_lists(current, desired, False), desired)

    def test_compare_lists_get_desired_diff(self):
        current = ["hello", "world"]
        desired = ["hello", "bar"]
        self.assertListEqual(ctera_common.compare_lists(current, desired, True), ["bar"])

    def test_get_modified_attributes_empty(self):
        current = dict(first='a', second='b')
        self.assertDictEqual(ctera_common.get_modified_attributes(None, {}), {})
        self.assertDictEqual(ctera_common.get_modified_attributes({}, {}), {})
        self.assertDictEqual(ctera_common.get_modified_attributes({}, current), {})

    def test_get_modified_attributes_equal(self):
        current = dict(first='a', second='b')
        self.assertDictEqual(ctera_common.get_modified_attributes(current, current), {})

    def test_get_modified_attributes_not_in_desired(self):
        current = dict(first='a', second='b')
        desired = dict(third='c')
        self.assertDictEqual(ctera_common.get_modified_attributes(current, desired), {})

    def test_get_modified_attributes_modified(self):
        current = dict(first='a', second='b', third='c')
        desired = dict(first='a', second='c')
        self.assertDictEqual(ctera_common.get_modified_attributes(current, desired), dict(second='c'))

    def test_get_modified_attributes_with_list(self):
        current = dict(first='a', second=['b'], third='c')
        desired = dict(first='a', second=['c'])
        self.assertDictEqual(ctera_common.get_modified_attributes(current, desired), dict(second=['c']))

    def test_get_modified_attributes_with__equal_list(self):
        current = dict(first='a', second=['b'], third='c')
        desired = dict(first='a', second=['b'], third='d')
        self.assertDictEqual(ctera_common.get_modified_attributes(current, desired), dict(third='d'))

    def test_set_result_single_change(self):
        self._test_set_result_only_changed(["changed"])

    def test_set_result_multiple_changes(self):
        self._test_set_result_only_changed(["changed", "again"])

    def _test_set_result_only_changed(self, changed_messages):
        ansible_return_value = ctera_common.AnsibleReturnValue()
        ansible_module = mock.MagicMock()
        ansible_module.ctera_return_value = mock.MagicMock(return_value=ansible_return_value)
        ctera_common.set_result(ansible_module, dict(changed=changed_messages, skipped=[]))
        self.assertTrue(ansible_return_value.param.changed)
        self.assertNotIn('skipped', ansible_return_value.as_dict())
        self.assertEqual(ansible_return_value.param.msg, "Changed: " + " ".join(changed_messages))

    def test_set_result_single_skip(self):
        self._test_set_result_only_skipped(["skipped"])

    def test_set_result_multiple_skips(self):
        self._test_set_result_only_changed(["skipped", "again"])

    def _test_set_result_only_skipped(self, skipped_messages):
        ansible_return_value = ctera_common.AnsibleReturnValue()
        ansible_module = mock.MagicMock()
        ansible_module.ctera_return_value = mock.MagicMock(return_value=ansible_return_value)
        ctera_common.set_result(ansible_module, dict(changed=[], skipped=skipped_messages))
        self.assertNotIn('changed', ansible_return_value.as_dict())
        self.assertTrue(ansible_return_value.param.skipped)
        self.assertEqual(ansible_return_value.param.msg, "Skipped: " + " ".join(skipped_messages))

    def test_set_result_both(self):
        changed_messages = ["changed"]
        skipped_messages = ["skipped"]
        ansible_return_value = ctera_common.AnsibleReturnValue()
        ansible_module = mock.MagicMock()
        ansible_module.ctera_return_value = mock.MagicMock(return_value=ansible_return_value)
        ctera_common.set_result(ansible_module, dict(changed=changed_messages, skipped=skipped_messages))
        self.assertNotIn('skipped', ansible_return_value.as_dict())
        self.assertTrue(ansible_return_value.param.changed)
        self.assertEqual(ansible_return_value.param.msg, "Changed: " + " ".join(changed_messages) + " Skipped: " + " ".join(skipped_messages))

    def test_set_result_empty(self):
        ansible_return_value = ctera_common.AnsibleReturnValue()
        ansible_module = mock.MagicMock()
        ansible_module.ctera_return_value = mock.MagicMock(return_value=ansible_return_value)
        ctera_common.set_result(ansible_module, dict(changed=[], skipped=[]))
        self.assertNotIn('changed', ansible_return_value.as_dict())
        self.assertNotIn('skipped', ansible_return_value.as_dict())
        self.assertNotIn('msg', ansible_return_value.as_dict())

    def test_object_exists_exists(self):
        get_return = dict(a=1)
        ctera_host = mock.MagicMock()
        ctera_host.get = mock.MagicMock(return_value=get_return)
        path = "path"
        exists, actual_return = ctera_common.object_exists(ctera_host, path)
        ctera_host.get.assert_called_once_with(path)
        self.assertTrue(exists)
        self.assertDictEqual(get_return, actual_return)

    def test_object_exists_does_not_exist(self):
        ctera_host = mock.MagicMock()
        ctera_host.get = mock.MagicMock(side_effect=CTERAException())
        path = "path"
        exists, actual_return = ctera_common.object_exists(ctera_host, path)
        ctera_host.get.assert_called_once_with(path)
        self.assertFalse(exists)
        self.assertEqual(actual_return, None)
