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
module: ctera_filer_smb
short_description: Manage the SMB configuration of the CTERA-Networks filer
description:
    - Enable/Disable/Modify the SMB configuration of the CTERA-Networks filer
version_added: "2.10"
extends_documentation_fragment:
    - ctera.ctera.filer

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  enabled:
    description: Enable SMB
    type: bool
    default: True
  packet_signing:
    description: Packet signing type
    type: str
    choices:
      - Disabled
      - If client agrees
      - Required
    default: Disabled
  idle_disconnect_time:
    description: Client Idle Disconnect Time (minutes)
    type: int
    default: 10
  compatibility_mode:
    description: Use compatibility mode
    type: bool
    default: False
  unix_extensions:
    description: Unix Extensions Mode
    type: bool
    default: True
  abe_enabled:
    description: Hide unreadable files and folders
    type: bool
    default: False

requirements:
    - cterasdk
'''

EXAMPLES = '''
- name: Configure SMB as default
  ctera_filer_smb:
    filer_host: "{{ ctera_filer_hostname }}"
    filer_user: "{{ ctera_filer_user }}"
    filer_password: "{{ ctera_filer_password }}"
'''

RETURN = r''' # '''

from ansible_collections.ctera.ctera.plugins.module_utils.ctera_filer_share_config_base import CteraFilerShareConfigBase


class CteraFilerSmb(CteraFilerShareConfigBase):
    def __init__(self):
        super().__init__(
            dict(
                packet_signing=dict(
                    type='str',
                    required=False,
                    default='Disabled',
                    choices=['Disabled', 'If client agrees', 'Required']
                ),
                idle_disconnect_time=dict(type='int', required=False, default=10),
                compatibility_mode=dict(type='bool', required=False, default=False),
                unix_extensions=dict(type='bool', required=False, default=True),
                abe_enabled=dict(type='bool', required=False, default=False),
            ),
        )

    @property
    def _share_type(self):
        return "SMB"

    @property
    def _manager(self):
        return self._ctera_filer.smb

    def _to_config_dict(self, config):
        return {k: v for k, v in config.__dict__.items() if not k.startswith("_")}


def main():  # pragma: no cover
    CteraFilerSmb().run()


if __name__ == '__main__':  # pragma: no cover
    main()
