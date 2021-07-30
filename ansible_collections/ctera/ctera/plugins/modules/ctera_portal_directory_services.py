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
module: ctera_portal_directory_services
short_description: CTERA Portal Active Directory configuration and management
description:
    - Connect, configure and disconnect CTERA Portal from active directory
    - If you only need to change the username and or password, set force_connect to True
extends_documentation_fragment:
    - ctera.ctera.vportal

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
  ssl:
    description: Connect to Active Directory over SSL
    type: bool
  krb:
    description: Connect to Active Directory over Kerberos
    type: bool
  domain_controllers:
    description: Configure a primary and a secondary domain controllers
    type: list
    elements: str
  force_reconnect:
    description: Disconnect and connect even if connected to the domain
    type: bool
    default: False

requirements:
    - cterasdk
'''

EXAMPLES = '''
- name: Directory Services - Connected
  ctera_portal_directory_services:
    domain: ctera.local
    username: admin
    password: admin
    domain_controllers:
      - "192.168.0.50"
      - "192.168.0.51"
    ctera_host: "{{ ctera_portal_hostname }}"
    ctera_user: "{{ ctera_portal_user }}"
    ctera_password: "{{ ctera_portal_password }}"
    ctera_trust_certificate: True

- name: Directory Services - Disonnected
  ctera_portal_directory_services:
    state: disconnected
    ctera_host: "{{ ctera_portal_hostname }}"
    ctera_user: "{{ ctera_portal_user }}"
    ctera_password: "{{ ctera_portal_password }}"
    ctera_trust_certificate: True
'''

RETURN = '''#'''

import ansible_collections.ctera.ctera.plugins.module_utils.ctera_common as ctera_common
from ansible_collections.ctera.ctera.plugins.module_utils.ctera_portal_base import CteraPortalBase

try:
    from cterasdk import CTERAException, portal_types
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common


class CteraPortalDirectoryServices(CteraPortalBase):
    _connect_params = ['domain', 'username', 'password', 'ou', 'ssl', 'krb', 'domain_controllers']

    def __init__(self):
        super().__init__(
            dict(
                state=dict(required=False, choices=['connected', 'disconnected'], default='connected'),
                domain=dict(type='str', required=False),
                username=dict(type='str', required=False),
                password=dict(type='str', required=False, no_log=True),
                ou=dict(type='str', required=False),
                ssl=dict(type='bool', required=False),
                krb=dict(type='bool', required=False),
                domain_controllers=dict(type='list', elements='str', required=False),
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
        connect_params = ctera_common.filter_parameters(self.parameters, CteraPortalDirectoryServices._connect_params)
        domain_controllers = self._create_domain_controllers_from_list(connect_params.pop('domain_controllers', None))
        self._ctera_portal.directoryservice.connect(**connect_params, domain_controllers=domain_controllers)
        self.ansible_module.ctera_return_value().changed().msg('Connected to Active Directory').put(**connect_params)

    @staticmethod
    def _create_domain_controllers_from_list(domain_controllers):
        if domain_controllers:
            if len(domain_controllers) > 2:
                raise CTERAException("Cannot set more than two static domain controllers")

            primary = domain_controllers[0] if len(domain_controllers) > 0 else None
            secondary = domain_controllers[1] if len(domain_controllers) > 1 else None
            return portal_types.DomainControllers(primary, secondary)
        return None

    def _handle_modify(self, connected_domain):
        if self._ctera_portal.directoryservice.connected() and \
           connected_domain['domain'] == self.parameters['domain'] and not self.parameters['force_reconnect']:
            self.ansible_module.ctera_return_value().msg('The Portal is already connected to Active Directory').put(domain=connected_domain['domain'])
            return
        self._ctera_portal.directoryservice.disconnect()
        self._do_connect()

    def _ensure_disconnected(self, connected_domain):
        if connected_domain['domain']:
            self._ctera_portal.directoryservice.disconnect()
            self.ansible_module.ctera_return_value().changed().msg('Successfully disconnected the Portal from Active Directory').put(
                domain=connected_domain['domain'])
        else:
            self.ansible_module.ctera_return_value().msg('The Portal is already not connected to Active Directory')

    def _get_connected_domain(self):
        return {'domain': self._ctera_portal.directoryservice.get_connected_domain()}


def main():  # pragma: no cover
    CteraPortalDirectoryServices().run()


if __name__ == '__main__':  # pragma: no cover
    main()
