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
module: ctera_filer_volume
short_description: CTERA-Networks Filer volume configuration and management
description:
    - Create, modify and delete volumes.
version_added: "2.10"
extends_documentation_fragment:
    - ctera.ctera.filer

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  state:
    description:
    - Whether the specified volume should exist or not.
    type: str
    choices: ['present', 'absent']
    default: 'present'
  name:
    description: The name of the volume
    required: True
    type: str
  filesystem:
    description: Filesystem to use, defaults to xfs
    required: False
    type: str
  size:
    description: Size of the volume in MBs, if not set the entire disk will be used
    required: False
    type: int
  device:
    description: Name of the device to use for the volume, can be left as None if there the gateway has only one
    required: False
    type: str
  passphrase:
    description: Passphrase for the volume
    required: False
    type: str

requirements:
    - cterasdk
'''

EXAMPLES = '''
- name: create new volume
  ctera_filer_volume:
    name: main
    filer_host: "{{ ctera_filer_hostname }}"
    filer_user: "{{ ctera_filer_user }}"
    filer_password: "{{ ctera_filer_password }}"
'''

RETURN = '''
name:
  description: Name of the newly created volume
  returned: when state is present
  type: str
  sample: main
size:
  description: Size of the newly created volume
  returned: when state is present
  type: str
  sample: 1024
'''

import ansible_collections.ctera.ctera.plugins.module_utils.ctera_common as ctera_common
from ansible_collections.ctera.ctera.plugins.module_utils.ctera_filer_base import CteraFilerBase

try:
    from cterasdk import CTERAException
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common


class CteraFilerVolume(CteraFilerBase):
    _create_params = ['name', 'size', 'filesystem', 'device', 'passphrase']

    def __init__(self):
        super().__init__(dict(
            state=dict(required=False, choices=['present', 'absent'], default='present'),
            name=dict(type='str', required=True),
            size=dict(type='int', required=False),
            filesystem=dict(type='str', required=False),
            device=dict(type='str', required=False),
            passphrase=dict(type='str', required=False, no_log=True)
        ))

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Volume management failed'

    def _execute(self):
        state = self.parameters.pop('state')
        volume = self._get_volume()
        if state == 'present':
            self._ensure_present(volume)
        else:
            self._ensure_absent(volume)

    def _ensure_present(self, volume):
        if volume:
            modified_attributes = ctera_common.get_modified_attributes(volume, self.parameters)
            if modified_attributes:
                desired_size = modified_attributes.get('size')
                if desired_size is not None:
                    self._ctera_filer.volumes.modify(self.parameters['name'], size=desired_size)
                    self.ansible_module.ctera_return_value().changed().msg('Volume  modified').put(
                        name=self.parameters['name'], size=desired_size)
                else:
                    self.ansible_module.ctera_return_value().skipped().msg('Currently you can only modify the volume size').put(
                        name=self.parameters['name'])
            else:
                self.ansible_module.ctera_return_value().skipped().msg('Volume details did not change').put(name=self.parameters['name'])
        else:
            create_params = {k: v for k, v in self.parameters.items() if k in CteraFilerVolume._create_params}
            self._ctera_filer.volumes.add(**create_params)
            self.ansible_module.ctera_return_value().changed().msg('Volume created').put(**create_params)

    def _ensure_absent(self, volume):
        if volume:
            self._ctera_filer.volumes.delete(self.parameters['name'])
            self.ansible_module.ctera_return_value().changed().msg('Volume deleted').put(name=self.parameters['name'])
        else:
            self.ansible_module.ctera_return_value().skipped().msg('Volume already does not exist').put(name=self.parameters['name'])

    def _get_volume(self):
        volume = None
        try:
            volume = self._ctera_filer.volumes.get(name=self.parameters['name'])
        except CTERAException as error:
            if error.response.code != 404:  # pylint: disable=no-member
                raise
        return self._to_volume_dict(volume) if volume else {}

    @staticmethod
    def _to_volume_dict(volume):
        volume_dict = {k: v for k, v in volume.__dict__.items() if not k.startswith("_")}
        return volume_dict


def main():  # pragma: no cover
    CteraFilerVolume().run()


if __name__ == '__main__':  # pragma: no cover
    main()
