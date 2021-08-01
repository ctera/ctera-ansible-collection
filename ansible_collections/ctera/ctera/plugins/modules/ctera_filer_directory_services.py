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
module: ctera_filer_directory_services
short_description: CTERA-Networks Filer active directory configuration and management
description:
    - Connect, Disconnect and Reconnect a CTERA-Networks filer to active directory
    - If you only need to change the username and or password, set force_connect to True
extends_documentation_fragment:
    - ctera.ctera.ctera

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  state:
    description: Whether the Edge Filer is connected to an Active Directory domain
    type: str
    choices:
      - connected
      - disconnected
    default: connected
  domain:
    description: Active Directory domain to connect to. Required if C(state) is connected
    type: str
  username:
    description: User Name to for communicating with the Active Directory Service. Required if C(state) is connected
    type: str
  password:
    description: Password of the user for communicating with the Active Directory Service. Required if C(state) is connected
    type: str
  ou:
    description: The OU path to use when connecting to the active directory services
    type: str
  force_reconnect:
    description: Disconnect and connect even if connected to the domain
    type: bool
    default: False

requirements:
    - cterasdk
'''

EXAMPLES = '''
- name: Directory Services - Connected
  ctera_filer_directory_services:
    domain: ctera.local
    username: admin
    password: admin
    ctera_host: "{{ ctera_filer_hostname }}"
    ctera_user: "{{ ctera_filer_user }}"
    ctera_password: "{{ ctera_filer_password }}"

- name: Directory Services - Disonnected
  ctera_filer_directory_services:
    state: disconnected
    ctera_host: "{{ ctera_filer_hostname }}"
    ctera_user: "{{ ctera_filer_user }}"
    ctera_password: "{{ ctera_filer_password }}"
'''

RETURN = '''
domain:
  description: Active Directory domain connected to
  returned: when state is connected, or when actualy disconnecting
  type: str
  sample: ad.example.com
username:
  description: User Name used to communicate with the Active Directory Service
  returned: when state is connected
  type: str
  sample: admin
ou:
  description: The OU path used when connecting to the active directory services
  returned: when state is connected
  type: str
  sample: Domain Controllers
'''

import ansible_collections.ctera.ctera.plugins.module_utils.ctera_common as ctera_common
from ansible_collections.ctera.ctera.plugins.module_utils.ctera_filer_base import CteraFilerBase


class CteraFilerDirectoryServices(CteraFilerBase):
    _connect_params = ['domain', 'username', 'password', 'ou']

    def __init__(self):
        super().__init__(
            dict(
                state=dict(required=False, choices=['connected', 'disconnected'], default='connected'),
                domain=dict(type='str', required=False),
                username=dict(type='str', required=False),
                password=dict(type='str', required=False, no_log=True),
                ou=dict(type='str', required=False),
                force_reconnect=dict(type='bool', required=False, default=False),
            ),
            required_if=[
                ('state', 'connected', ['domain', 'username', 'password'])
            ]
        )

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Active Directory management failed.'

    def _execute(self):
        state = self.parameters.pop('state')
        connected_domain = self._get_connected_domain()
        if state == 'connected':
            self._ensure_connected(connected_domain)
        else:
            self._ensure_disconnected(connected_domain)

    def _ensure_connected(self, connected_domain):
        if connected_domain['domain']:
            self._handle_modify(connected_domain)
        else:
            self._do_connect()

    def _do_connect(self):
        connect_params = ctera_common.filter_parameters(self.parameters, CteraFilerDirectoryServices._connect_params)
        self._ctera_filer.directoryservice.connect(**connect_params)
        self.ansible_module.ctera_return_value().changed().msg('Connected to Active Directory').put(**connect_params)

    def _handle_modify(self, connected_domain):
        if self._ctera_filer.directoryservice.connected() and \
                connected_domain['domain'] == self.parameters['domain'] and \
                not self.parameters['force_reconnect']:
            self.ansible_module.ctera_return_value().msg('The Edge Filer is already connected to Active Directory').put(domain=connected_domain['domain'])
            return
        self._ctera_filer.directoryservice.disconnect()
        self._do_connect()

    def _ensure_disconnected(self, connected_domain):
        if connected_domain['domain']:
            self._ctera_filer.directoryservice.disconnect()
            self.ansible_module.ctera_return_value().changed().msg('Successfully disconnected the Edge Filer from Active Directory').put(
                domain=connected_domain['domain'])
        else:
            self.ansible_module.ctera_return_value().msg('The Edge Filer is already not connected to Active Directory')

    def _get_connected_domain(self):
        return self._to_domain_dict(self._ctera_filer.directoryservice.get_connected_domain())

    @staticmethod
    def _to_domain_dict(config):
        return {k: v for k, v in config.__dict__.items() if not k.startswith("_")}


def main():  # pragma: no cover
    CteraFilerDirectoryServices().run()


if __name__ == '__main__':  # pragma: no cover
    main()
