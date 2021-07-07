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
module: ctera_filer_domain_controllers
short_description: Set static domain controllers
description:
    - Set static domain controllers to be used by the CTERA Edge Filer when connecting to directory services
extends_documentation_fragment:
    - ctera.ctera.ctera

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  state:
    description:
    - Whether the specified domain controller configuration should exist or not.
    type: str
    choices: ['present', 'absent']
    default: 'present'
  domain_controllers:
    description: List of ip addresses, hostnames, FQDN's or '*'
    required: False
    type: list
    elements: str

requirements:
    - cterasdk
'''

EXAMPLES = '''
- name: Set static domain controllers
  ctera.ctera.ctera_filer_domain_controllers:
    domain_controllers:
    - "192.168.100.50"
    - "192.168.100.51"
    - "*"
    ctera_host: "{{ ctera_filer_hostname }}"
    ctera_user: "{{ ctera_filer_user }}"
    ctera_password: "{{ ctera_filer_password }}"

- name: Remove static domain controllers
  ctera.ctera.ctera_filer_domain_controllers:
    state: absent
    ctera_host: "{{ ctera_filer_hostname }}"
    ctera_user: "{{ ctera_filer_user }}"
    ctera_password: "{{ ctera_filer_password }}"
'''

RETURN = ''' # '''

from ansible_collections.ctera.ctera.plugins.module_utils.ctera_filer_base import CteraFilerBase


class CteraFilerDomainControllers(CteraFilerBase):

    def __init__(self):
        super().__init__(
            dict(
                state=dict(required=False, choices=['present', 'absent'], default='present'),
                domain_controllers=dict(type='list', elements='str', required=False)
            ),
            required_if=[('state', 'present', ['domain_controllers'])]
        )

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Failed to update domain controllers'

    def _execute(self):
        state = self.parameters.pop('state')
        current_domain_controllers = self._ctera_filer.directoryservice.get_static_domain_controller()
        if state == 'present':
            self._ensure_present(current_domain_controllers)
        else:
            self._ensure_absent(current_domain_controllers)

    def _ensure_present(self, current_domain_controllers):
        new_domain_controllers = ' '.join(self.parameters['domain_controllers'])
        if new_domain_controllers != current_domain_controllers:
            self._ctera_filer.directoryservice.set_static_domain_controller(new_domain_controllers)
            self.ansible_module.ctera_return_value().changed().msg('Static domain controllers set').put(domain_controllers=new_domain_controllers)
        else:
            self.ansible_module.ctera_return_value().skipped().msg(
                'Static domain controllers configuration did not change').put(domain_controllers=current_domain_controllers)

    def _ensure_absent(self, current_domain_controllers):
        if current_domain_controllers:
            self._ctera_filer.directoryservice.remove_static_domain_controller()
            self.ansible_module.ctera_return_value().changed().msg('Static domain controllers removed').put(domain_controllers=current_domain_controllers)
        else:
            self.ansible_module.ctera_return_value().skipped().msg('No static domain controllers configuration exists')


def main():  # pragma: no cover
    CteraFilerDomainControllers().run()


if __name__ == '__main__':  # pragma: no cover
    main()
