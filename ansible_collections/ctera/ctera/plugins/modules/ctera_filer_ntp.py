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
module: ctera_filer_ntp
short_description: Manage the NTP configuration of the CTERA Edge filer
description:
    - Set the NTP configuration of the CTERA Edge filer
extends_documentation_fragment:
    - ctera.ctera.ctera

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  state:
    description: Whether the NTP service should be enabled or not
    type: str
    choices:
      - enabled
      - disabled
    default: enabled
  servers:
    description: A list of NTP servers
    required: False
    type: list
    elements: str

requirements:
    - cterasdk
'''

EXAMPLES = '''
- name: Configure NTP servers
  ctera_filer_ntp:
    servers:
      - "0.pool.ntp.org"
      - "1.pool.ntp.org"
      - "2.pool.ntp.org"
    ctera_host: "{{ ctera_filer_hostname }}"
    ctera_user: "{{ ctera_filer_user }}"
    ctera_password: "{{ ctera_filer_password }}"
'''

RETURN = r''' # '''

import ansible_collections.ctera.ctera.plugins.module_utils.ctera_common as ctera_common
from ansible_collections.ctera.ctera.plugins.module_utils.ctera_filer_base import CteraFilerBase

try:
    from cterasdk import gateway_enum
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common


class CteraFilerNtp(CteraFilerBase):

    def __init__(self):
        super().__init__(
            dict(
                state=dict(required=False, choices=['enabled', 'disabled'], default='enabled'),
                servers=dict(type='list', elements='str', required=False)
            ),
            required_if=[
                ('state', 'enabled', ['servers'])
            ]
        )

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Failed to update NTP configuration'

    def _execute(self):
        state = self.parameters.pop('state')
        ntp_config = self._ctera_filer.ntp.get_configuration()
        if state == 'enabled':
            self._ensure_enabled(ntp_config)
        else:
            self._ensure_disabled(ntp_config)

    def _ensure_enabled(self, ntp_config):
        ntp_servers = self.parameters['servers']
        if ntp_config.NTPMode == gateway_enum.Mode.Enabled:
            if ctera_common.compare_lists(ntp_config.NTPServer, ntp_servers, False):
                self._ctera_filer.ntp.enable(ntp_servers)
                self.ansible_module.ctera_return_value().changed().msg('Updated NTP configuration').put(servers=ntp_servers)
            else:
                self.ansible_module.ctera_return_value().skipped().msg('NTP configuration did not change').put(servers=ntp_servers)
        else:
            self._ctera_filer.ntp.enable(ntp_servers)
            self.ansible_module.ctera_return_value().changed().msg('Enabled NTP').put(servers=ntp_servers)

    def _ensure_disabled(self, ntp_config):
        if ntp_config.NTPMode == gateway_enum.Mode.Disabled:
            self.ansible_module.ctera_return_value().skipped().msg('NTP is already disabled')
        else:
            self._ctera_filer.ntp.disable()
            self.ansible_module.ctera_return_value().changed().msg('Disabled NTP')


def main():  # pragma: no cover
    CteraFilerNtp().run()


if __name__ == '__main__':  # pragma: no cover
    main()
