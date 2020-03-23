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
module: ctera_filer_location
short_description: Set the location of the CTERA-Networks filer
description:
    - Set the location of the CTERA-Networks filer
version_added: "2.10"
extends_documentation_fragment:
    - ctera.ctera.filer

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  location:
    description: The location for the CTERA-Networks filer
    required: True
    type: str

requirements:
    - cterasdk
'''

EXAMPLES = '''
- name: Set Location
  ctera_filer_location:
    location: Somewhere
    filer_host: "{{ ctera_filer_hostname }}"
    filer_user: "{{ ctera_filer_user }}"
    filer_password: "{{ ctera_filer_password }}"
'''

RETURN = '''
previous_location:
  description: The CTERA Network filer's location before the change
  type: str
  returned: When location is changed
  sample: BeforeChange
current_location:
  description: The CTERA Network filer's location after the change
  type: str
  returned: Always
  sample: AfterChange
'''

from ansible_collections.ctera.ctera.plugins.module_utils.ctera_filer_base import CteraFilerBase


class CteraFilerLocation(CteraFilerBase):

    def __init__(self):
        super().__init__(dict(location=dict(type='str', required=True)))

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Failed to update location'

    def _execute(self):
        location = self.parameters['location']
        current_location = self._ctera_filer.config.get_location()
        if location != current_location:
            self._ctera_filer.config.set_location(location)
            self.ansible_module.ctera_return_value().changed().msg('Changed location').put(previous_location=current_location, current_location=location)
        else:
            self.ansible_module.ctera_return_value().msg('No update required to the current location').put(current_location=current_location)


def main():  # pragma: no cover
    CteraFilerLocation().run()


if __name__ == '__main__':  # pragma: no cover
    main()
