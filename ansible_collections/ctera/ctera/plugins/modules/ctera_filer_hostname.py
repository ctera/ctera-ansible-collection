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
module: ctera_filer_hostname
short_description: Set the hostname of  the CTERA-Networks filer
description:
    - Set the hostname of  the CTERA-Networks filer
version_added: "2.10"
extends_documentation_fragment:
    - ctera.ctera.filer

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  hostname:
    description: The hostname for the CTERA-Networks filer
    required: True
    type: str

requirements:
    - cterasdk
'''

EXAMPLES = '''
- name: Set Hostname
  ctera_filer_hostname:
    hostname: Example
    filer_host: "{{ ctera_filer_hostname }}"
    filer_user: "{{ ctera_filer_user }}"
    filer_password: "{{ ctera_filer_password }}"
'''

RETURN = '''
previous_hostname:
  description: The CTERA Network filer's hostname before the change
  type: str
  returned: When hostname is changed
  sample: BeforeChange
current_hostname:
  description: The CTERA Network filer's hostname after the change
  type: str
  returned: Always
  sample: AfterChange
'''

from ansible_collections.ctera.ctera.plugins.module_utils.ctera_filer_base import CteraFilerBase


class CteraFilerHostname(CteraFilerBase):

    def __init__(self):
        super().__init__(dict(hostname=dict(type='str', required=True)))

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Failed to update hostname'

    def _execute(self):
        hostname = self.parameters['hostname']
        current_hostname = self._ctera_filer.config.get_hostname()
        if hostname != current_hostname:
            self._ctera_filer.config.set_hostname(hostname)
            self.ansible_module.ctera_return_value().changed().msg('Changed hostname').put(previous_hostname=current_hostname, current_hostname=hostname)
        else:
            self.ansible_module.ctera_return_value().msg('No update required to the current hostname').put(current_hostname=current_hostname)


def main():  # pragma: no cover
    CteraFilerHostname().run()


if __name__ == '__main__':  # pragma: no cover
    main()
