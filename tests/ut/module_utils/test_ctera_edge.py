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

try:
    from cterasdk import CTERAException
except ImportError:  # pragma: no cover
    pass

import ansible_collections.ctera.ctera.plugins.module_utils.ctera_edge as ctera_edge
from tests.ut.mocks import ansible_module_mock
from tests.ut.base import BaseTest


class TestCteraEdge(BaseTest):  #pylint: disable=too-many-public-methods

    def setUp(self):
        super().setUp()
        ansible_module_mock.mock_bases(self, ctera_edge.GatewayAnsibleModule)

        self.gateway_class_mock = self.patch_call("ansible_collections.ctera.ctera.plugins.module_utils.ctera_edge.Gateway")
        self.gateway_object_mock = self.gateway_class_mock.return_value

        self.ansible_return_value_class_mock = self.patch_call(
            "ansible_collections.ctera.ctera.plugins.module_utils.ctera_edge.ctera_common.AnsibleReturnValue"
        )
        self.ansible_return_value_object_mock = self.ansible_return_value_class_mock.return_value

    def test_no_cterasdk(self):
        cterasdk_imp_err = "Failed to import"
        self.patch_call("ansible_collections.ctera.ctera.plugins.module_utils.ctera_edge.ctera_common.HAS_CTERASDK", new=False)
        self.patch_call("ansible_collections.ctera.ctera.plugins.module_utils.ctera_edge.ctera_common.CTERASDK_IMP_ERR", new=cterasdk_imp_err)
        gateway_ansible_module = ctera_edge.GatewayAnsibleModule(dict())
        self.assertDictEqual(gateway_ansible_module.fail_dict, dict(msg=mock.ANY, exception=cterasdk_imp_err))

    def test_ctera_filer_with_login(self):
        self.gateway_object_mock.login = mock.MagicMock(return_value=None)
        gateway_ansible_module = ctera_edge.GatewayAnsibleModule(dict())
        self.gateway_class_mock.assert_called_once_with('192.168.1.1')
        gateway_ansible_module.ctera_filer()
        self.gateway_object_mock.login.assert_called_once_with('admin', 'password')

    def test_ctera_filer_login_failed(self):
        self.gateway_object_mock.login = mock.MagicMock(side_effect=CTERAException())
        gateway_ansible_module = ctera_edge.GatewayAnsibleModule(dict())
        self.gateway_class_mock.assert_called_once_with('192.168.1.1')
        gateway_ansible_module.ctera_filer()
        self.gateway_object_mock.login.assert_called_once_with('admin', 'password')

    def test_ctera_filer_no_login(self):
        self.gateway_object_mock.login = mock.MagicMock(return_value=None)
        gateway_ansible_module = ctera_edge.GatewayAnsibleModule(dict())
        self.gateway_class_mock.assert_called_once_with('192.168.1.1')
        gateway_ansible_module.ctera_filer(login=False)
        self.gateway_object_mock.login.assert_not_called()

    def test_ctera_filer_logout(self):
        self.gateway_object_mock.logout = mock.MagicMock(return_value=None)
        gateway_ansible_module = ctera_edge.GatewayAnsibleModule(dict())
        self.gateway_class_mock.assert_called_once_with('192.168.1.1')
        gateway_ansible_module.ctera_logout()
        self.gateway_object_mock.logout.assert_called_once_with()

    def test_ctera_return_value(self):
        gateway_ansible_module = ctera_edge.GatewayAnsibleModule(dict())
        self.gateway_class_mock.assert_called_once_with('192.168.1.1')
        ansible_return_value = gateway_ansible_module.ctera_return_value()
        self.assertEqual(self.ansible_return_value_object_mock, ansible_return_value)

    def test_ctera_exit_success(self):
        self._test_ctera_exit(False)

    def test_ctera_exit_failure(self):
        self._test_ctera_exit(True)

    def _test_ctera_exit(self, has_failed):
        self.ansible_return_value_object_mock.has_failed.return_value = has_failed
        expected_dict = dict(msg='Success')
        self.ansible_return_value_object_mock.as_dict.return_value = expected_dict
        gateway_ansible_module = ctera_edge.GatewayAnsibleModule(dict())
        self.gateway_class_mock.assert_called_once_with('192.168.1.1')
        gateway_ansible_module.ctera_exit()
        if has_failed:
            self.assertDictEqual(gateway_ansible_module.exit_dict, {})
            self.assertDictEqual(gateway_ansible_module.fail_dict, expected_dict)
        else:
            self.assertDictEqual(gateway_ansible_module.exit_dict, expected_dict)
            self.assertDictEqual(gateway_ansible_module.fail_dict, {})

    def test_filer_trust_certificate_true(self):
        self._test_filer_trust_certificate(True)

    def test_filer_trust_certificate_false(self):
        self._test_filer_trust_certificate(False)

    def _test_filer_trust_certificate(self, trust):
        ansible_module_mock.filer_trust_certificate = trust
        ctera_edge.GatewayAnsibleModule(dict())
        self.assertEqual(ctera_edge.config.http['ssl'], 'Trust' if trust else 'Consent')
