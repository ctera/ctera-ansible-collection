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
module: ctera_filer_timezone
short_description: Set the timezone of  the CTERA-Networks filer
description:
    - Set the timezone of  the CTERA-Networks filer
version_added: "2.10"
extends_documentation_fragment:
    - ctera.ctera.filer

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  timezone:
    description: The timezone for the CTERA-Networks filer
    required: True
    type: str

requirements:
    - cterasdk
'''

EXAMPLES = '''
- name: Set Hostname
  ctera_filer_timezone:
    timezone: "(GMT-05:00) Eastern Time (US , Canada)"
    filer_host: "{{ ctera_filer_hostname }}"
    filer_user: "{{ ctera_filer_user }}"
    filer_password: "{{ ctera_filer_password }}"
'''

RETURN = '''
previous_timezone:
  description: The CTERA Network filer's timezone before the change
  type: str
  returned: When timezone is changed
  sample: "(GMT-05:00) Eastern Time (US , Canada)"
current_timezone:
  description: The CTERA Network filer's timezone after the change
  type: str
  returned: Always
  sample: "(GMT-06:00) Central Time (US , Canada)"
'''

from ansible_collections.ctera.ctera.plugins.module_utils.ctera_filer_base import CteraFilerBase


class CteraFilerTimezone(CteraFilerBase):

    def __init__(self):
        super().__init__(dict(timezone=dict(type='str', required=True)))

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Failed to update timezone'

    def _execute(self):
        timezone = self.parameters['timezone']
        current_timezone = self._ctera_filer.timezone.get_timezone()
        if timezone != current_timezone:
            self._ctera_filer.timezone.set_timezone(timezone)
            self.ansible_module.ctera_return_value().changed().msg('Changed timezone').put(previous_timezone=current_timezone, current_timezone=timezone)
        else:
            self.ansible_module.ctera_return_value().msg('No update required to the current timezone').put(current_timezone=current_timezone)


def main():  # pragma: no cover
    CteraFilerTimezone().run()


if __name__ == '__main__':  # pragma: no cover
    main()
