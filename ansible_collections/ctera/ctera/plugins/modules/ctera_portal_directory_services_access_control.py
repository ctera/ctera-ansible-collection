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
module: ctera_portal_directory_services_access_control
short_description: CTERA Portal directory services access control rules
description:
    - Set access control rules for domain users and groups
extends_documentation_fragment:
    - ctera.ctera.vportal

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  state:
    description:
    - Whether the specified access control rule should exist or not.
    type: str
    choices: ['present', 'absent']
    default: 'present'
  acl:
    description: List of Access Control Entries
    type: list
    elements: dict
    suboptions:
      principal_type:
        description: The type of entry (domain user or group)
        type: str
        required: True
        choices:
        - group
        - user
      domain:
        description: The domain name
        type: str
        required: True
      name:
        description: The name of the domain user or group
        type: str
        required: True
      role:
        description: The role
        type: str
        choices:
        - ReadWriteAdmin
        - ReadOnlyAdmin
        - Support
        - EndUser
        - Disabled
        required: True

'''

EXAMPLES = r'''
- name: Set domain access control rules
  ctera_portal_directory_services_access_control:
    acl:
      - { principal_type: 'group', domain: 'demo.local', name: 'support', role: 'ReadWriteAdmin' }
      - { principal_type: 'user', domain: 'demo.local', name: 'jsmith', perm: 'EndUser' }
    ctera_host: "{{ ctera_portal_hostname }}"
    ctera_user: "{{ ctera_portal_user }}"
    ctera_password: "{{ ctera_portal_password }}"
    ctera_trust_certificate: True
'''

RETURN = r'''#'''


import os

import ansible_collections.ctera.ctera.plugins.module_utils.ctera_common as ctera_common
from ansible_collections.ctera.ctera.plugins.module_utils.ctera_portal_base import CteraPortalBase

try:
    from cterasdk import CTERAException, portal_types
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common


class CteraPortalDirectoryServicesAccessControl(CteraPortalBase):
    _access_control_params = ['acl']

    def __init__(self):
        roles = ['ReadWriteAdmin', 'ReadOnlyAdmin', 'Support', 'EndUser', 'Disabled']
        super().__init__(dict(
            state=dict(required=False, choices=['present', 'absent'], default='present'),
            acl=dict(
                type='list',
                required=False,
                elements='dict',
                options=dict(
                    principal_type=dict(type='str', required=True, choices=['group', 'user']),
                    domain=dict(required=True),
                    name=dict(required=True),
                    role=dict(required=True, choices=roles)
                )
            )
        ))

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Active Directory access control management failed'

    def _execute(self):
        state = self.parameters.pop('state')
        current_acl = self._get_access_control_rules()
        new_acl = self._create_access_control_index(self._create_access_control_entries(self.parameters['acl']))

        if state == 'present':
            self._ensure_present(current_acl, new_acl)
        else:
            self._ensure_absent(current_acl)

    def _get_access_control_rules(self):
        acl = None
        try:
            acl = self._ctera_portal.directoryservice.get_access_control()
        except CTERAException as error:
            if error.response.code != 404:  # pylint: disable=no-member
                raise
        return self._create_access_control_index(acl)

    def _create_access_control_entries(self, acl):
        access_control_entries = []
        for ace in acl:
            principal_type = ace['principal_type']
            domain = ace['domain']
            name = ace['name']
            role = ace['role']
            if principal_type == 'group':
                access_control_entries.append(portal_types.AccessControlEntry(portal_types.GroupAccount(name, domain), role))
            elif principal_type == 'user':
                access_control_entries.append(portal_types.AccessControlEntry(portal_types.UserAccount(name, domain), role))
            else:
                raise CTERAException('Invalid principal type.')
        return access_control_entries

    def _create_access_control_index(self, acl):
        access_control_index = dict()
        for ace in acl:
            access_control_index['#'.join([str(ace.account), ace.role])] = ace
        return access_control_index

    def _ensure_present(self, current_acl, new_acl):
        diff = ctera_common.compare_lists(list(current_acl.keys()), list(new_acl.keys()), get_list_diff=False)
        if diff:
            self._ctera_portal.directoryservice.set_access_control(new_acl.values())
            self.ansible_module.ctera_return_value().changed().msg('Configured access control rules')
        else:
            self.ansible_module.ctera_return_value().skipped().msg('Access control details did not change')

    def _ensure_absent(self, current_acl):
        if current_acl:
            self._ctera_portal.directoryservice.set_access_control([])
            self.ansible_module.ctera_return_value().changed().msg('Removed access control entries')
        else:
            self.ansible_module.ctera_return_value().skipped().msg('No access control rules exist')


def main():  # pragma: no cover
    CteraPortalDirectoryServicesAccessControl().run()


if __name__ == '__main__':  # pragma: no cover
    main()
