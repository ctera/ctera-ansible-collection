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

from ansible_collections.ctera.ctera.plugins.module_utils.ctera_filer_base import CteraFilerBase
import ansible_collections.ctera.ctera.plugins.module_utils.ctera_common as ctera_common

try:
    from cterasdk import gateway_enum
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common


class CteraFilerShareConfigBase(CteraFilerBase):
    def __init__(self, ansible_module_args, **kwars):
        ansible_module_args.update(dict(enabled=dict(type='bool', required=False, default=True)))
        super().__init__(ansible_module_args, **kwars)

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Failed to manage %s configuration' % self._share_type

    @property
    def _share_type(self):  # pragma: no cover
        raise NotImplementedError("Implementing class must implement _share_type")

    @property
    def _mode_field(self):
        return 'mode'

    @property
    def _manager(self):  # pragma: no cover
        raise NotImplementedError("Implementing class must implement _manager")

    def _to_config_dict(self, config):  # pragma: no cover
        raise NotImplementedError("Implementing class must implement _to_config_dict")

    def _execute(self):
        enabled = self.parameters.pop('enabled')
        current_config = self._get_current_config()
        if enabled:
            self._ensure_enabled(current_config)
        else:
            self._ensure_disabled(current_config)

    def _get_current_config(self):
        return self._to_config_dict(self._manager.get_configuration())

    def _ensure_enabled(self, current_config):
        messages = {
            'changed': [],
            'skipped': []
        }
        if current_config[self._mode_field] == gateway_enum.Mode.Enabled:
            messages['skipped'].append('%s already enabled' % self._share_type)
        else:
            self._manager.enable()
            messages['changed'].append('%s enabled' % self._share_type)

        current_config = self._get_current_config()
        modified_attributes = ctera_common.get_modified_attributes(current_config, self.parameters)
        if modified_attributes:
            self._manager.modify(**modified_attributes)
            messages['changed'].append('%s configuration updated' % self._share_type)
        else:
            messages['skipped'].append('%s configuration already up to date' % self._share_type)

        ctera_common.set_result(self.ansible_module, messages)

    def _ensure_disabled(self, current_config):
        if current_config[self._mode_field] == gateway_enum.Mode.Enabled:
            self._manager.disable()
            self.ansible_module.ctera_return_value().changed().msg('%s server disabled' % self._share_type)
        else:
            self.ansible_module.ctera_return_value().msg('%s server already disabled' % self._share_type)
