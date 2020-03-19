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

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
import ansible_collections.ctera.ctera.plugins.module_utils.ctera_common as ctera_common

try:
    from cterasdk import Gateway, CTERAException, tojsonstr
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common


class GatewayAnsibleModule(AnsibleModule):

    default_argument_spec = {
        'filer_host': dict(type='str', required=True),
        'filer_user': dict(type='str', required=True),
        'filer_password': dict(type='str', required=True, no_log=True)
    }

    def __init__(
            self,
            argument_spec,
            bypass_checks=False,
            no_log=False,
            mutually_exclusive=None,
            required_together=None,
            required_one_of=None,
            add_file_common_args=False,
            supports_check_mode=False,
            required_if=None,
            required_by=None):  # pylint: disable=too-many-arguments
        argument_spec.update(GatewayAnsibleModule.default_argument_spec)
        super().__init__(argument_spec, bypass_checks=bypass_checks, no_log=no_log, mutually_exclusive=mutually_exclusive, required_together=required_together,
                         required_one_of=required_one_of, add_file_common_args=add_file_common_args, supports_check_mode=supports_check_mode,
                         required_if=required_if, required_by=required_by or {})
        if not ctera_common.HAS_CTERASDK:
            self.fail_json(msg=missing_required_lib('CTERASDK'), exception=ctera_common.CTERASDK_IMP_ERR)
        self._ctera_filer = Gateway(self.params['filer_host'])
        self._ctera_return_value = ctera_common.AnsibleReturnValue()

    def ctera_filer(self, login=True):
        if login:
            self.ctera_login()
        return self._ctera_filer

    def ctera_login(self):
        try:
            self._ctera_filer.login(self.params['filer_user'], self.params['filer_password'])
        except CTERAException as error:
            self._ctera_return_value.failed().msg('Login failed. Exception: %s' % tojsonstr(error, False))
            self.ctera_exit()

    def ctera_logout(self):
        self._ctera_filer.logout()

    def ctera_return_value(self):
        return self._ctera_return_value

    def ctera_exit(self):
        if self._ctera_return_value.has_failed():
            self.fail_json(**self._ctera_return_value.as_dict())
        else:
            self.exit_json(**self._ctera_return_value.as_dict())
