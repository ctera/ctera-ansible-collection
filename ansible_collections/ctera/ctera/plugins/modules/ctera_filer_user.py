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
module: ctera_filer_user
short_description: CTERA-Networks Filer user configuration and management
description:
    - Create, modify and delete users.
version_added: "2.10"
extends_documentation_fragment:
    - ctera.ctera.filer

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
  username:
    description: The name of the user
    required: True
    type: str
  email:
    description: The e-mail address of the user
    type: str
  full_name:
    description: The full name of the user
    type: str
  password:
    description:
    - The password of the user
    - Required when C(state=present) and the user does not exist
    - If the user exists, the new password will be set
    type: str
  uid:
    description: ID for the user
    type: str
'''

EXAMPLES = '''
- name: create local user
  ctera_filer_user:
    username: 'alice'
    email: 'walice@wonderland.com'
    full_name: 'Alice Wonderland'
    password: 'su@p3rsecret!!'
    filer_host: "{{ ctera_filer_hostname }}"
    filer_user: "{{ ctera_filer_user }}"
    filer_password: "{{ ctera_filer_password }}"
'''

RETURN = '''
username:
  description: User name of the user
  returned: when state is present
  type: str
  sample: admin
full_name:
  description: Full name of the user
  returned: when state is present
  type: str
  sample: Administrator
email:
  description: E-mail address of the user
  returned: when state is present
  type: str
  sample: admin@example.com
uid:
  description: ID of the user
  returned: when state is present
  type: str
  sample: XXX
'''

import ansible_collections.ctera.ctera.plugins.module_utils.ctera_common as ctera_common
from ansible_collections.ctera.ctera.plugins.module_utils.ctera_filer_base import CteraFilerBase

try:
    from cterasdk import CTERAException
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common


class CteraFilerUser(CteraFilerBase):
    _create_params = ['username', 'password', 'full_name', 'email', 'uid']

    def __init__(self):
        super().__init__(dict(
            state=dict(required=False, choices=['present', 'absent'], default='present'),
            username=dict(type='str', required=True),
            password=dict(type='str', required=False, no_log=True),
            full_name=dict(type='str', required=False),
            email=dict(type='str', required=False),
            uid=dict(type='str', required=False)
        ))

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
            user = self._ctera_filer.users.get(name=self.parameters['username'])
        except CTERAException as error:
            if error.response.code != 404:  # pylint: disable=no-member
                raise
        return self._to_user_dict(user) if user else None

    def _ensure_present(self, user):
        if user:
            modified_attributes = ctera_common.get_modified_attributes(user, self.parameters)
            if modified_attributes:
                self._ctera_filer.users.modify(self.parameters['username'], **modified_attributes)
                self.ansible_module.ctera_return_value().changed().msg('User modified').put(username=self.parameters['username'], **modified_attributes)
            else:
                self.ansible_module.ctera_return_value().skipped().msg('User details did not change').put(username=self.parameters['username'])
        else:
            create_params = {k: v for k, v in self.parameters.items() if k in CteraFilerUser._create_params}
            if create_params.get('password') is None:
                raise CTERAException(message="Cannot create new user without a password")
            self._ctera_filer.users.add(**create_params)
            self.ansible_module.ctera_return_value().changed().msg('User created').put(**create_params)

    def _ensure_absent(self, user):
        if user:
            self._ctera_filer.users.delete(self.parameters['username'])
            self.ansible_module.ctera_return_value().changed().msg('User deleted').put(username=self.parameters['username'])
        else:
            self.ansible_module.ctera_return_value().skipped().msg('User already does not exist').put(username=self.parameters['username'])

    @staticmethod
    def _to_user_dict(user):
        user_dict = {k: v for k, v in user.__dict__.items() if not k.startswith("_")}
        full_name = user_dict.pop('fullName', None)
        if full_name is not None:
            user_dict['full_name'] = full_name
        return user_dict


def main():  # pragma: no cover
    CteraFilerUser().run()


if __name__ == '__main__':  # pragma: no cover
    main()
