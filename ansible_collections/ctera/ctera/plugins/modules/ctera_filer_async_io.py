#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, CTERA Networks Ltd.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'CTERA'
}

DOCUMENTATION = '''
---
module: ctera_filer_async_io
short_description: CTERA-Networks Filer Async-I/O configuration and management
description:
    - Enable or Disable Async-I/O.
version_added: "2.10"
extends_documentation_fragment:
    - ctera.ctera.filer

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  enabled:
    description:
    - Whether Async-I/O should be enabled or disabled
    type: bool
    default: True
'''

EXAMPLES = '''
- name: Enable Async-I/O
  ctera_filer_async_io:
    filer_host: "{{ ctera_filer_hostname }}"
    filer_user: "{{ ctera_filer_user }}"
    filer_password: "{{ ctera_filer_password }}"

- name: Disable Async-I/O
  ctera_filer_async_io:
    enabled: False
    filer_host: "{{ ctera_filer_hostname }}"
    filer_user: "{{ ctera_filer_user }}"
    filer_password: "{{ ctera_filer_password }}"
'''

RETURN = r''' # '''

from ansible_collections.ctera.ctera.plugins.module_utils.ctera_filer_base import CteraFilerBase


class CteraFilerAsyncIO(CteraFilerBase):
    def __init__(self):
        super().__init__(dict(
            enabled=dict(type='bool', required=False, default=True),
        ))

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Failed to %s asynchronous I/O.' % ("enable" if self.parameters['enabled'] else "disable")

    def _execute(self):
        is_enabled = self._ctera_filer.aio.is_enabled()
        if self.parameters['enabled'] == is_enabled:
            self.ansible_module.ctera_return_value().skipped().msg("asynchronous I/O is already %s" % ("enabled" if is_enabled else "disabled"))
            return

        if self.parameters['enabled']:
            self._ctera_filer.aio.enable()
        else:
            self._ctera_filer.aio.disable()
        self.ansible_module.ctera_return_value().changed().msg('%s asynchronous I/O' % ("Enabled" if self.parameters['enabled'] else "Disabled"))


def main():  # pragma: no cover
    CteraFilerAsyncIO().run()


if __name__ == '__main__':  # pragma: no cover
    main()
