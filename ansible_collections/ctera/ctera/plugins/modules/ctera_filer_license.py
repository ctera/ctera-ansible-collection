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
module: ctera_filer_license
short_description: Apply a license on a CTERA-Networks filer
description:
    - Apply a license on a CTERA-Networks filer
version_added: "2.10"
extends_documentation_fragment:
    - ctera.ctera.filer

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  license:
    description: CTERA Network filer license type to apply
    required: True
    type: str
    choices:
      - EV8
      - EV16
      - EV32
      - EV64
      - EV128

requirements:
    - cterasdk
'''

EXAMPLES = '''
- name: apply license
  ctera_filer_apply_license:
    license: EV16
    filer_host: "{{ ctera_filer_hostname }}"
    filer_user: "{{ ctera_filer_user }}"
    filer_password: "{{ ctera_filer_password }}"
'''

RETURN = '''
license:
  description: The CTERA Network filer license that was applied
  returned: when state is present
  type: str
  sample: EV16
'''

from ansible_collections.ctera.ctera.plugins.module_utils.ctera_filer_base import CteraFilerBase


class CteraFilerLicense(CteraFilerBase):

    def __init__(self):
        super().__init__(dict(license=dict(type='str', required=True, choices=['EV8', 'EV16', 'EV32', 'EV64', 'EV128'])))

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'An error occurred while trying to apply license'

    def _execute(self):
        current_license = self._ctera_filer.licenses.get()
        if current_license != self.parameters['license']:
            self._ctera_filer.licenses.apply(self.parameters['license'])
            self.ansible_module.ctera_return_value().changed().msg('License applied').put(license=self.parameters['license'])
        else:
            self.ansible_module.ctera_return_value().skipped().msg('License has not changed').put(license=self.parameters['license'])


def main():  # pragma: no cover
    CteraFilerLicense().run()


if __name__ == '__main__':  # pragma: no cover
    main()
