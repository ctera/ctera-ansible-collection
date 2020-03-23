#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, CTERA Networks Ltd.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: ctera_filer_syslog
short_description: Manage the Syslog configuration of the CTERA-Networks filer
description:
    - Enable/Disable/Modify the Syslog configuration of the CTERA-Networks filer
version_added: "2.10"
extends_documentation_fragment:
    - ctera.ctera.filer

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  enabled:
    description: Enable Syslog
    type: bool
    default: True
  server:
    description: Syslog server address. Required if C(enabled=True)
    type: str
  port:
    description: Syslog server port
    required: False
    type: int
    default: 514
  proto:
    description: Syslog server communication protocol
    type: str
    choices:
      - TCP
      - UDP
    default: UDP
  min_severity:
    description: Minimal log severity to report tp syslog
    type: str
    choices:
      - emergency
      - alert
      - critical
      - error
      - warning
      - notice
      - info
      - debug
    default: info

requirements:
    - cterasdk
'''

EXAMPLES = '''
- name: Configure Syslog
  ctera_filer_syslog:
    server: www.example.com
    filer_host: "{{ ctera_filer_hostname }}"
    filer_user: "{{ ctera_filer_user }}"
    filer_password: "{{ ctera_filer_password }}"
'''

RETURN = '''
server:
  description: The address of the syslog server
  type: str
  returned: When enabled
  sample: www.example.com
'''

from ansible_collections.ctera.ctera.plugins.module_utils.ctera_filer_base import CteraFilerBase
import ansible_collections.ctera.ctera.plugins.module_utils.ctera_common as ctera_common

try:
    from cterasdk import gateway_enum
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common


class CteraFilerSyslog(CteraFilerBase):
    _enable_params = ['server', 'port', 'proto', 'min_severity']

    def __init__(self):
        super().__init__(
            dict(
                enabled=dict(type='bool', required=False, default=True),
                server=dict(type='str', required=False),
                port=dict(type='int', required=False, default=514),
                proto=dict(type='str', required=False, default='UDP', choices=['TCP', 'UDP']),
                min_severity=dict(
                    type='str',
                    required=False,
                    default='info',
                    choices=['emergency', 'alert', 'critical', 'error', 'warning', 'notice', 'info', 'debug']
                )
            ),
            required_if=[('enabled', True, ['server'])]
        )

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Failed to update hostname'

    def _execute(self):
        enabled = self.parameters.pop('enabled')
        current_config = self._get_current_config()
        if enabled:
            self._ensure_enabled(current_config)
        else:
            self._ensure_disabled(current_config)

    def _ensure_enabled(self, current_config):
        if current_config['mode'] == gateway_enum.Mode.Enabled:
            modified_attributes = ctera_common.get_modified_attributes(current_config, self.parameters)
            if modified_attributes:
                self._ctera_filer.syslog.modify(**modified_attributes)
                self.ansible_module.ctera_return_value().changed().msg('Updated Syslog server configuration').put(server=self.parameters['server'])
            else:
                self.ansible_module.ctera_return_value().msg('Syslog server details did not change').put(server=self.parameters['server'])
        else:
            enable_params = {k: v for k, v in self.parameters.items() if k in CteraFilerSyslog._enable_params}
            self._ctera_filer.syslog.enable(**enable_params)
            self.ansible_module.ctera_return_value().changed().msg('Syslog server enabled')

    def _ensure_disabled(self, current_config):
        if current_config['mode'] == gateway_enum.Mode.Enabled:
            self._ctera_filer.syslog.disable()
            self.ansible_module.ctera_return_value().changed().msg('Syslog server disabled')
        else:
            self.ansible_module.ctera_return_value().msg('Syslog server already disabled')

    def _get_current_config(self):
        return self._to_config_dict(self._ctera_filer.syslog.get_configuration())

    @staticmethod
    def _to_config_dict(config):
        config_dict = {k: v for k, v in config.__dict__.items() if not k.startswith("_")}
        config_dict['min_severity'] = config_dict.pop('minSeverity', None)
        return config_dict


def main():  # pragma: no cover
    CteraFilerSyslog().run()


if __name__ == '__main__':  # pragma: no cover
    main()
