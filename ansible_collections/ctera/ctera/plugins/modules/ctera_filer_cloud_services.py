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
module: ctera_filer_cloud_services
short_description: Cloud services configuration and management
description:
    - Connect, Disconnect and Reconnect a CTERA filer to the cloud serivces
version_added: "2.10"
extends_documentation_fragment:
    - ctera.ctera.filer

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  state:
    description: Whether the Cloud Services by Connected, Disconnected
    type: str
    choices:
      - connected
      - disconnected
    default: connected
  server:
    description: IP Address or FQDN of CTERA Portal
    required: True
    type: str
  user:
    description: CTERA Portal user account name
    required: True
    type: str
  password:
    description: CTERA Portal user account password
    required: True
    type: str
  ctera_license:
    description: Filer license type
    required: False
    type: str
    choices:
      - EV8
      - EV16
      - EV32
      - EV64
      - EV128
    default: EV16
  force_reconnect:
    description: Execute reconnect if connection details have not changed
    type: bool
    default: False
  sso:
    description: Enable/Disable remote SSO for Portal administrators
    type: bool
    default: False
  trust_certificate:
    description: Trust unverified certificates
    type: bool
    default: False

requirements:
    - cterasdk
'''

EXAMPLES = '''
- name: connect cloud services
  ctera_filer_connect_cloud_services:
    server: portal.example.com
    user: admin
    password: admin
    ctera_license: EV32
    filer_host: "{{ ctera_filer_hostname }}"
    filer_user: "{{ ctera_filer_user }}"
    filer_password: "{{ ctera_filer_password }}"
'''

RETURN = '''
address:
  description: IP Address or FQDN of CTERA Portal
  returned: when state is present
  type: str
  sample: portal.example.com
user:
  description: CTERA Portal user account name
  returned: when state is present
  type: str
  sample: admin
ctera_license:
  description: The active license type
  returned: when state is present
  type: str
  sample: EV16
'''

import ansible_collections.ctera.ctera.plugins.module_utils.ctera_common as ctera_common
from ansible_collections.ctera.ctera.plugins.module_utils.ctera_filer_base import CteraFilerBase

try:
    from cterasdk import CTERAException, tojsonstr, config
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common


class CteraFilerCloudServices(CteraFilerBase):
    _connect_params = ['server', 'user', 'password', 'ctera_license']

    def __init__(self):
        super().__init__(dict(
            state=dict(required=False, choices=['connected', 'disconnected'], default='connected'),
            server=dict(type='str', required=True),
            user=dict(type='str', required=True),
            password=dict(type='str', required=True, no_log=True),
            ctera_license=dict(type='str', required=False, default='EV16', choices=['EV8', 'EV16', 'EV32', 'EV64', 'EV128']),
            force_reconnect=dict(type='bool', required=False, default=False),
            sso=dict(type='bool', required=False, default=False),
            trust_certificate=dict(type='bool', required=False, default=False)
        ))

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Cloud Services management failed.'

    def _execute(self):
        if self.parameters['trust_certificate']:
            config.connect['ssl'] = 'Trust'

        state = self.parameters.pop('state')
        status = self._ctera_filer.services.get_status()
        if state == 'connected':
            self._ensure_connected(status)
        else:
            if status.connected:
                self._ctera_filer.services.disconnect()
                self.ansible_module.ctera_return_value().changed().msg('Successfully disconnected the Filer from the Cloud Services').put(
                    server=self.parameters['server'])
            else:
                self.ansible_module.ctera_return_value().skipped().msg('The Filer is already disconnected from the Cloud Services')

    def _ensure_connected(self, status):
        messages = {
            'changed': [],
            'skipped': []
        }
        if status.connected:
            if not self._handle_modify(status, messages):
                return
        else:
            self._do_connect()
            messages['changed'].append('Successfully connected the Filer to the Cloud Services')
        self._ensure_sso_state(messages)
        self.ansible_module.ctera_return_value().put(server=self.parameters['server'])
        ctera_common.set_result(self.ansible_module, messages)

    def _ensure_sso_state(self, messages):
        sso_state = self._ctera_filer.services.sso_enabled()
        if sso_state == self.parameters['sso']:
            messages['skipped'].append("SSO already %s" % ('enabled' if sso_state else 'disabled'))
            return

        if self.parameters['sso']:
            self._ctera_filer.services.enable_sso()
        else:
            self._ctera_filer.services.disable_sso()
        messages['changed'].append("SSO was %s" % ('enabled' if self.parameters['sso'] else 'disabled'))

    def _do_connect(self):
        connect_params = {k: v for k, v in self.parameters.items() if k in CteraFilerCloudServices._connect_params}
        self._ctera_filer.services.connect(**connect_params)

    def _handle_modify(self, status, messages):
        if self._connection_parameters_changed(status):
            self._ctera_filer.services.disconnect()
            try:
                self._do_connect()
                messages['changed'].append('Successfully modified the Filer connection to the Cloud Services')
                self.ansible_module.ctera_return_value().put(previous_server=status.server_address)
            except CTERAException as error:
                self.ansible_module.ctera_return_value().failed().msg(
                    'Failed to connect to new Cloud Services. Filer is now disconnected Exception: %s' % tojsonstr(error, False)).put(
                        server=self.parameters['server'])
                return False
        else:
            if self.parameters['force_reconnect']:
                self._ctera_filer.services.reconnect()
                messages['changed'].append('Successfully reconnected the Filer to the Cloud Services')
            else:
                messages['skipped'].append('The Filer is already connected to the Cloud Services')
        return True

    def _connection_parameters_changed(self, status):
        return self.parameters['server'] != status.server_address


def main():  # pragma: no cover
    CteraFilerCloudServices().run()


if __name__ == '__main__':  # pragma: no cover
    main()
