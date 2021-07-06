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
module: ctera_portal_timezone
short_description: Set the timezone of CTERA Portal
description:
    - Set the timezone of CTERA Portal
extends_documentation_fragment:
    - ctera.ctera.vportal

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  timezone:
    description: The timezone for CTERA Portal
    required: True
    type: str

requirements:
    - cterasdk
'''

EXAMPLES = '''
- name: Set Timezone
  ctera.ctera.ctera_portal_timezone:
    timezone: "(GMT-05:00) Eastern Time (US , Canada)"
    ctera_host: "{{ ctera_portal_hostname }}"
    ctera_user: "{{ ctera_portal_user }}"
    ctera_password: "{{ ctera_portal_password }}"
'''

RETURN = '''
previous_timezone:
  description: The timezone before the change
  type: str
  returned: When timezone is changed
  sample: "(GMT-05:00) Eastern Time (US , Canada)"
current_timezone:
  description: The timezone after the change
  type: str
  returned: Always
  sample: "(GMT-06:00) Central Time (US , Canada)"
'''

from ansible_collections.ctera.ctera.plugins.module_utils.ctera_portal_base import CteraPortalBase


class CteraPortalTimezone(CteraPortalBase):

    def __init__(self):
        super().__init__(dict(timezone=dict(type='str', required=True)))

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Failed to update timezone'

    def _execute(self):
        timezone = self.parameters['timezone']
        current_timezone = self._ctera_portal.settings.global_settings.get_timezone()
        if timezone != current_timezone:
            self._ctera_portal.settings.global_settings.set_timezone(timezone)
            self.ansible_module.ctera_return_value().changed().msg('Changed timezone').put(previous_timezone=current_timezone, current_timezone=timezone)
        else:
            self.ansible_module.ctera_return_value().msg('No update required to the current timezone').put(current_timezone=current_timezone)


def main():  # pragma: no cover
    CteraPortalTimezone().run()


if __name__ == '__main__':  # pragma: no cover
    main()
