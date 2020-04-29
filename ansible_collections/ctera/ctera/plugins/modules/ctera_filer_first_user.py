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
module: ctera_filer_first_user
short_description: First user on a CTERA-Networks filer
description:
    - First user on a CTERA-Networks filer
    - Please note that the first user cannot be modified.
version_added: "2.10"
extends_documentation_fragment:
    - ctera.ctera.filer

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  email:
    description: E-mail address of the new user
    type: str

requirements:
    - cterasdk
'''

EXAMPLES = '''
- name: first local user
  ctera_filer_add_first_user:
    filer_host: "{{ ctera_filer_hostname }}"
    filer_user: "{{ ctera_filer_user }}"
    filer_password: "{{ ctera_filer_password }}"
'''

RETURN = '''
user:
  description: User name of the newly created user
  returned: Always
  type: str
  sample: admin
'''

from ansible_collections.ctera.ctera.plugins.module_utils.ctera_filer_base import CteraFilerBase


class CteraFilerFirstUser(CteraFilerBase):
    def __init__(self):
        super().__init__(dict(email=dict(type='str', required=False)), login=False)

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'First user management failed'

    def _execute(self):
        logininfo = self._ctera_filer.get('/nosession/logininfo')

        if logininfo.isfirstlogin:
            self._ctera_filer.users.add_first_user(self.parameters['filer_user'], self.parameters['filer_password'], email=self.parameters.get('email', ''))
            self.ansible_module.ctera_return_value().changed().msg('User created')
        else:
            self._ctera_filer = self.ansible_module.ctera_filer(login=True)
            self.ansible_module.ctera_return_value().msg('First user was already created')
        self.ansible_module.ctera_return_value().put(user=self.parameters['filer_user'])


def main():  # pragma: no cover
    CteraFilerFirstUser().run()


if __name__ == '__main__':  # pragma: no cover
    main()
