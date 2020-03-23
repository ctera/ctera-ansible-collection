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
module: ctera_filer_telnet
short_description: CTERA-Networks Filer Telnet configuration and management
description:
    - Enable or Disable Telnet.
version_added: "2.10"
extends_documentation_fragment:
    - ctera.ctera.filer

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  enabled:
    description:
    - Whether Telnet should be enabled or disabled
    type: bool
    default: True
  code:
    description:
    - Telnet Authorization code. Required if C(enabled) is True
    type: str
'''

EXAMPLES = '''
- name: Enable Telnet
  ctera_filer_telnet:
    code: abcdefgh
    filer_host: "{{ ctera_filer_hostname }}"
    filer_user: "{{ ctera_filer_user }}"
    filer_password: "{{ ctera_filer_password }}"

- name: Disable Telnet
  ctera_filer_telnet:
    enabled: False
    filer_host: "{{ ctera_filer_hostname }}"
    filer_user: "{{ ctera_filer_user }}"
    filer_password: "{{ ctera_filer_password }}"
'''

RETURN = r''' # '''

from ansible_collections.ctera.ctera.plugins.module_utils.ctera_filer_base import CteraFilerBase


class CteraFilerTelnet(CteraFilerBase):
    def __init__(self):
        super().__init__(
            dict(
                enabled=dict(type='bool', required=False, default=True),
                code=dict(type='str', required=False, no_log=True)
            ),
            required_if=[
                ('enabled', True, ['code'])
            ]
        )

    @property  # pragma: no cover
    def _generic_failure_message(self):
        return 'Failed to %s Telnet.' % ("enable" if self.parameters['enabled'] else "disable")

    def _execute(self):
        if self.parameters['enabled']:
            self._ctera_filer.telnet.enable(self.parameters['code'])
        else:
            self._ctera_filer.telnet.disable()
        self.ansible_module.ctera_return_value().changed().msg('Telnet daemon %s' % ('enabled' if self.parameters['enabled'] else 'disabled'))


def main():  # pragma: no cover
    CteraFilerTelnet().run()


if __name__ == '__main__':  # pragma: no cover
    main()
