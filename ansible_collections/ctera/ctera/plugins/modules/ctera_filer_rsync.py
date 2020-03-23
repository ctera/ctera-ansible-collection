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
module: ctera_filer_rsync
short_description: Manage the RSync configuration of the CTERA-Networks filer
description:
    - Enable/Disable/Modify the RSync configuration of the CTERA-Networks filer
version_added: "2.10"
extends_documentation_fragment:
    - ctera.ctera.filer

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  enabled:
    description: Enable RSync
    type: bool
    default: True
  port:
    description: RSync Port
    type: int
    default: 873
  max_connections:
    description: Maximum Connections
    type: int
    default: 25
requirements:
    - cterasdk
'''

EXAMPLES = '''
- name: Configure RSync as default
  ctera_filer_rsync:
    filer_host: "{{ ctera_filer_hostname }}"
    filer_user: "{{ ctera_filer_user }}"
    filer_password: "{{ ctera_filer_password }}"
'''

RETURN = r''' # '''

from ansible_collections.ctera.ctera.plugins.module_utils.ctera_filer_share_config_base import CteraFilerShareConfigBase


class CteraFilerRSync(CteraFilerShareConfigBase):
    def __init__(self):
        super().__init__(
            dict(
                port=dict(type='int', required=False, default=873),
                max_connections=dict(type='int', required=False, default=25),
            )
        )

    @property
    def _share_type(self):
        return "RSync"

    @property
    def _manager(self):
        return self._ctera_filer.rsync

    @property
    def _mode_field(self):
        return 'server'

    def _to_config_dict(self, config):
        return dict(
            server=config.server,
            port=config.port,
            max_connections=config.maxConnections,
        )


def main():  # pragma: no cover
    CteraFilerRSync().run()


if __name__ == '__main__':  # pragma: no cover
    main()
