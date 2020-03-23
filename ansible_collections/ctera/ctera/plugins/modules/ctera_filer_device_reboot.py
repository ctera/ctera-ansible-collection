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
module: ctera_filer_device_reboot
short_description: Reboot the CTERA-Networks filer
description:
    - Reboot the CTERA-Networks filer
version_added: "2.10"
extends_documentation_fragment:
    - ctera.ctera.filer

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  wait:
    description:
    - Wait until the operation completes
    type: bool
    default: False

requirements:
    - cterasdk
'''

EXAMPLES = '''
- name: Reboot
  ctera_filer_device_reboot:
    filer_host: "{{ ctera_filer_hostname }}"
    filer_user: "{{ ctera_filer_user }}"
    filer_password: "{{ ctera_filer_password }}"
'''

RETURN = r''' # '''

from ansible_collections.ctera.ctera.plugins.module_utils.ctera_filer_base import CteraFilerBase


class CteraFilerDeviceReboot(CteraFilerBase):

    def __init__(self):
        super().__init__(
            dict(
                wait=dict(type='bool', required=False, default=False)
            )
        )

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Failed to execute device reboot'

    def _execute(self):
        wait = self.parameters['wait']
        self._ctera_filer.power.reboot(wait)
        if wait:
            self.ansible_module.ctera_return_value().msg('Filer is up and running')
        else:
            self.ansible_module.ctera_return_value().msg('Rebooting device')


def main():  # pragma: no cover
    CteraFilerDeviceReboot().run()


if __name__ == '__main__':  # pragma: no cover
    main()
