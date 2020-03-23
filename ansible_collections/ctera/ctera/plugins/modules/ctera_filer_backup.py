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
module: ctera_filer_backup
short_description: Configure backup settings for a CTERA-Networks filer. Currently, you cannot modify or disable the configuration
description:
    - Configure backup settings for a CTERA-Networks filer
version_added: "2.10"
extends_documentation_fragment:
    - ctera.ctera.filer

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  passphrase:
    description: Passphrase for the backup
    type: str

requirements:
    - cterasdk
'''

EXAMPLES = '''
- name: Backup with passphrase
  ctera_filer_backup:
    passphrase: ThisIsAGr8Password!
'''

RETURN = r''' # '''

from ansible_collections.ctera.ctera.plugins.module_utils.ctera_filer_base import CteraFilerBase


class CteraFilerBackup(CteraFilerBase):
    def __init__(self):
        super().__init__(dict(passphrase=dict(type='str', required=False, no_log=True)))

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Failed configuring cloud backup'

    def _execute(self):
        if self._ctera_filer.backup.is_configured():
            self.ansible_module.ctera_return_value().msg('Cloud Backup is already configured')
        else:
            self._ctera_filer.backup.configure(self.parameters['passphrase'])
            self.ansible_module.ctera_return_value().changed().msg('Configured cloud backup')


def main():  # pragma: no cover
    CteraFilerBackup().run()


if __name__ == '__main__':  # pragma: no cover
    main()
