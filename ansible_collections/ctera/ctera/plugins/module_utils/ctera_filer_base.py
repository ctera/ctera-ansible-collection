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

from ansible_collections.ctera.ctera.plugins.module_utils.ctera_edge import GatewayAnsibleModule
import ansible_collections.ctera.ctera.plugins.module_utils.ctera_common as ctera_common

try:
    from cterasdk import CTERAException, tojsonstr
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common


class CteraFilerBase(object):

    def __init__(self, ansible_module_args, supports_check_mode=False, required_if=None, login=True, required_by=None):
        required_if = required_if or []
        self.ansible_module = GatewayAnsibleModule(
            ansible_module_args,
            supports_check_mode=supports_check_mode,
            required_if=required_if,
            required_by=required_by
        )
        self.parameters = ctera_common.get_parameters(self.ansible_module.params)
        self._ctera_filer = None
        self._login = login

    def run(self):
        self._ctera_filer = self.ansible_module.ctera_filer(login=self._login)
        try:
            self._execute()
        except CTERAException as error:
            self.ansible_module.ctera_return_value().failed().msg(self._generic_failure_message + (' Exception: %s' % tojsonstr(error, False)))
        self.ansible_module.ctera_logout()
        self.ansible_module.ctera_exit()

    @property
    def _generic_failure_message(self):  # pragma: no cover
        raise NotImplementedError("Implementing classes must implemen _generic_failure_message")

    def _execute(self):  # pragma: no cover
        raise NotImplementedError("Implementing classes must implemen _execute")
