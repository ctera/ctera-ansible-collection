#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, CTERA Networks Ltd.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'CTERA'
}

DOCUMENTATION = '''
---
module: ctera_filer_snmp
short_description: CTERA Edge Filer SNMP configuration and management
description:
    - Enable or Disable SNMP.
extends_documentation_fragment:
    - ctera.ctera.ctera

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  enabled:
    description:
    - Whether SNMP should be enabled or disabled
    type: bool
    default: True
  port:
    description:
    - SNMP server port
    type: int
  community_str:
    description:
    - SNMP v2c community string
    type: str
  username:
    description:
    - SNMP v3 authentication user name
    type: str
  password:
    description:
    - SNMP v3 authentication user password
    type: str
  update_password:
    description: If True, the password will be updated
    type: bool
    default: False
'''

EXAMPLES = '''
- name: Enable SNMP
  ctera.ctera.ctera_filer_snmp:
    enabled: True
    port: 8161
    community_str: 'MpPcKl2sArSdTLZ4URj45'
    username: 'admin2'
    password: 'password1!'
    update_password: False
    ctera_host: "{{ ctera_filer_hostname }}"
    ctera_user: "{{ ctera_filer_user }}"
    ctera_password: "{{ ctera_filer_password }}"

- name: Disable SNMP
  ctera.ctera.ctera_filer_snmp:
    enabled: False
    ctera_host: "{{ ctera_filer_hostname }}"
    ctera_user: "{{ ctera_filer_user }}"
    ctera_password: "{{ ctera_filer_password }}"
'''

RETURN = r''' # '''

import ansible_collections.ctera.ctera.plugins.module_utils.ctera_common as ctera_common
from ansible_collections.ctera.ctera.plugins.module_utils.ctera_filer_base import CteraFilerBase


class CteraFilerSNMP(CteraFilerBase):
    _enable_params = ['port', 'community_str', 'username', 'password']

    def __init__(self):
        super().__init__(dict(
            enabled=dict(type='bool', required=False, default=True),
            port=dict(type='int', required=False),
            community_str=dict(type='str', required=False),
            username=dict(type='str', required=False),
            password=dict(type='str', required=False, no_log=True),
            update_password=dict(type='bool', default=False, no_log=True)
        ))

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Failed to %s SNMP.' % ("enable" if self.parameters['enabled'] else "disable")

    def _execute(self):
        enabled = self.parameters.pop('enabled')
        snmp_enabled = self._ctera_filer.snmp.is_enabled()
        if enabled:
            update_password = self.parameters.pop('update_password')
            if snmp_enabled:
                if not update_password:
                    self.parameters.pop('password', None)
                modified_attributes = ctera_common.get_modified_attributes(self._get_snmp_config(), self.parameters)
                if modified_attributes:
                    self._ctera_filer.snmp.modify(**modified_attributes)
                    self.ansible_module.ctera_return_value().changed().msg('Modified SNMP configuration')
                else:
                    self.ansible_module.ctera_return_value().skipped().msg("No change made to the SNMP configuration")
            else:
                enable_params = {k: v for k, v in self.parameters.items() if k in CteraFilerSNMP._enable_params}
                self._ctera_filer.snmp.enable(**enable_params)
                self.ansible_module.ctera_return_value().changed().msg('Enabled SNMP')
        else:
            if snmp_enabled:
                self._ctera_filer.snmp.disable()
                self.ansible_module.ctera_return_value().changed().msg('Disabled SNMP')
            else:
                self.ansible_module.ctera_return_value().skipped().msg("SNMP is already disabled")

    def _get_snmp_config(self):
        snmp_config = self._ctera_filer.snmp.get_configuration()
        return dict(
            port=snmp_config.port,
            community_str=snmp_config.readCommunity,
            username=snmp_config.snmpV3.username if snmp_config.snmpV3 is not None else None,
            password=snmp_config.snmpV3.password if snmp_config.snmpV3 is not None else None
        )


def main():  # pragma: no cover
    CteraFilerSNMP().run()


if __name__ == '__main__':  # pragma: no cover
    main()
