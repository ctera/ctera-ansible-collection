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
module: ctera_filer_array
short_description: CTERA-Networks Filer array configuration and management
description:
    - Create, modify and delete RAID arrays.
extends_documentation_fragment:
    - ctera.ctera.ctera

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  state:
    description:
    - Whether the specified array should exist or not.
    type: str
    choices: ['present', 'absent']
    default: 'present'
  array_name:
    description: The name of the array
    required: True
    type: str
  level:
    description: The array type
    type: str
    choices: ['linear', '0', '1', '5', '6']
  members:
    description: A list of drive names
    type: list
    elements: str

'''

EXAMPLES = '''
- name: Create RAID array
  ctera_filer_array:
    array_name: 'array'
    level: '1'
    members:
      - VIRT2
      - VIRT3
- name: Remove RAID array
  ctera_filer_array:
    state: 'absent'
    array_name: 'array'

'''

RETURN = '''
name:
  description: Name of the newly created array
  returned: when state is present
  type: str
  sample: array
level:
  description: The array level
  returned: when state is present
  type: str
  sample: 'linear'
members:
  description: The drive names that are members of the array. If not passed, an array will be created using all available drives
  returned: when state is present
  type: list
  sample: array
  required: False
'''

import ansible_collections.ctera.ctera.plugins.module_utils.ctera_common as ctera_common
from ansible_collections.ctera.ctera.plugins.module_utils.ctera_filer_base import CteraFilerBase

try:
    from cterasdk import CTERAException
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common


class CteraFilerArray(CteraFilerBase):
    _create_params = ['array_name', 'level', 'members']

    def __init__(self):
        super().__init__(
            dict(
                state=dict(required=False, choices=['present', 'absent'], default='present'),
                array_name=dict(type='str', required=True),
                level=dict(type='str', choices=['linear', '0', '1', '5', '6']),
                members=dict(type='list', elements='str', required=False)
            ),
            required_if=[('state', 'present', ['level'])]
        )

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Array management failed'

    def _execute(self):
        state = self.parameters.pop('state')
        array = self._get_array()
        if state == 'present':
            self._ensure_present(array)
        else:
            self._ensure_absent(array)

    def _get_array(self):
        array = None
        try:
            array = self._ctera_filer.array.get(name=self.parameters['array_name'])
        except CTERAException as error:
            if error.response.code != 404:  # pylint: disable=no-member
                raise
        return self._to_array_dict(array) if array else {}

    @staticmethod
    def _to_array_dict(array):
        array_dict = {k: v for k, v in array.__dict__.items() if not k.startswith("_")}
        return array_dict

    def _ensure_present(self, array):
        if not array:
            create_params = {k: v for k, v in self.parameters.items() if k in CteraFilerArray._create_params}
            self._ctera_filer.array.add(**create_params)
            self.ansible_module.ctera_return_value().changed().msg('Array created').put(**create_params)
        else:
            self.ansible_module.ctera_return_value().skipped().msg('Already already exists').put(name=self.parameters['array_name'])

    def _ensure_absent(self, array):
        if array:
            self._ctera_filer.array.delete(self.parameters['array_name'])
            self.ansible_module.ctera_return_value().changed().msg('Array deleted').put(name=self.parameters['array_name'])
        else:
            self.ansible_module.ctera_return_value().skipped().msg('Array already does not exist').put(name=self.parameters['array_name'])


def main():  # pragma: no cover
    CteraFilerArray().run()


if __name__ == '__main__':  # pragma: no cover
    main()
