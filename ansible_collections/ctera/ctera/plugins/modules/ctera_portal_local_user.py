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
module: ctera_portal_local_user
short_description: CTERA-Networks Portal user configuration and management
description:
    - Create, modify and delete users.
extends_documentation_fragment:
    - ctera.ctera.vportal

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  state:
    description:
    - Whether the specified user should exist or not.
    type: str
    choices: ['present', 'absent']
    default: 'present'
  name:
    description: The name of the user
    required: True
    type: str
  email:
    description: The e-mail address of the user
    type: str
  first_name:
    description: The first name of the user
    type: str
  last_name:
    description: The first name of the user
    type: str
  password:
    description:
    - The password of the user
    - Required when C(state=present) and the user does not exist
    - If the user exists, the new password will be set
    type: str
  update_password:
    description: If True, and user exists, the password will be updated
    type: bool
    default: False
  role:
    description:
    - User role of the new user
    type: str
    choices: ['Disabled', 'EndUser', 'ReadWriteAdmin', 'ReadOnlyAdmin', 'Support']
    default: 'Disabled'
  company:
    description: The name of the company of the user
    type: str
  comment:
    description: Additional comment for the user
    type: str
  password_change:
    description:
    - Whether to enforce a password change
    - Pass a string in the format of '%Y-%m-%d' for a specific date, integer for days from creation, or True for immediate , defaults to False.
    type: raw
    default: False

'''

EXAMPLES = '''
- name: create local user
  ctera_portal_local_user:
    name: 'alice'
    email: 'walice@wonderland.com'
    first_name: 'Alice'
    last_name: 'Wonderland'
    password: 'su@p3rsecret!!'
    role: 'ReadWriteAdmin'
    ctera_host: "{{ ctera_portal_hostname }}"
    ctera_user: "{{ ctera_portal_user }}"
    ctera_password: "{{ ctera_portal_password }}"
'''

RETURN = '''
name:
  description: User name of the user
  returned: when state is present
  type: str
  sample: admin
'''
import datetime

import ansible_collections.ctera.ctera.plugins.module_utils.ctera_common as ctera_common
from ansible_collections.ctera.ctera.plugins.module_utils.ctera_portal_base import CteraPortalBase

try:
    from cterasdk import CTERAException, portal_types
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common


class CteraPortalLocalUser(CteraPortalBase):
    _create_params = ['name', 'email', 'first_name', 'last_name', 'password', 'role', 'company', 'comment', 'password_change']

    def __init__(self):
        super().__init__(
            dict(
                state=dict(required=False, choices=['present', 'absent'], default='present'),
                name=dict(type='str', required=True),
                email=dict(type='str', required=False),
                first_name=dict(type='str', required=False),
                last_name=dict(type='str', required=False),
                password=dict(type='str', required=False, no_log=True),
                update_password=dict(type='bool', default=False),
                role=dict(type='str', required=False, choices=['Disabled', 'EndUser', 'ReadWriteAdmin', 'ReadOnlyAdmin', 'Support'], default='Disabled'),
                company=dict(type='str', required=False),
                comment=dict(type='str', required=False),
                password_change=dict(type='raw', required=False, default=False, no_log=True)
            )
        )

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'User management failed'

    def _execute(self):
        state = self.parameters.pop('state')
        user = self._get_user()
        if state == 'present':
            self._ensure_present(user)
        else:
            self._ensure_absent(user)

    def _get_user(self):
        user = None
        try:
            user = self._ctera_portal.users.get(portal_types.UserAccount(self.parameters['name']), include=CteraPortalLocalUser._create_params)
        except CTERAException:
            pass
        return self._to_user_dict(user) if user else None

    @staticmethod
    def _translate_password_change(password_change):
        if isinstance(password_change, str):
            return datetime.datetime.strptime(password_change, '%Y-%m-%d').date()
        return password_change

    def _ensure_present(self, user):
        update_password = self.parameters.pop('update_password')
        if user:
            self.parameters.pop('password_change', None)
            if not update_password:
                self.parameters.pop('password', None)
            modified_attributes = ctera_common.get_modified_attributes(user, self.parameters)
            if modified_attributes:
                self._ctera_portal.users.modify(self.parameters['name'], **modified_attributes)
                self.ansible_module.ctera_return_value().changed().msg('User modified').put(name=self.parameters['name'])
            else:
                self.ansible_module.ctera_return_value().skipped().msg('User details did not change').put(name=self.parameters['name'])
        else:
            self.parameters['password_change'] = self._translate_password_change(self.parameters['password_change'])
            create_params = {k: v for k, v in self.parameters.items() if k in CteraPortalLocalUser._create_params}
            if create_params.get('password') is None:
                raise CTERAException(message="Cannot create new user without a password")
            self._ctera_portal.users.add(**create_params)
            self.ansible_module.ctera_return_value().changed().msg('User created').put(**create_params)

    def _ensure_absent(self, user):
        if user:
            self._ctera_portal.users.delete(portal_types.UserAccount(self.parameters['name']))
            self.ansible_module.ctera_return_value().changed().msg('User deleted').put(name=self.parameters['name'])
        else:
            self.ansible_module.ctera_return_value().skipped().msg('User already does not exist').put(name=self.parameters['name'])

    @staticmethod
    def _to_user_dict(user):
        return {k: v for k, v in user.__dict__.items() if not k.startswith("_")}


def main():  # pragma: no cover
    CteraPortalLocalUser().run()


if __name__ == '__main__':  # pragma: no cover
    main()
