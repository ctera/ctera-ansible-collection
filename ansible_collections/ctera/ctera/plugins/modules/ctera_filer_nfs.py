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
module: ctera_filer_nfs
short_description: Manage the NFS configuration of the CTERA-Networks filer
description:
    - Enable/Disable/Modify the NFS configuration of the CTERA-Networks filer
version_added: "2.10"
extends_documentation_fragment:
    - ctera.ctera.filer

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  enabled:
    description: Enable NFS
    type: bool
    default: True
  async_write:
    description: Use asynchronous writes
    type: bool
    default: True
  aggregate_writes:
    description: Aggregate write requests
    type: bool
    default: True

requirements:
    - cterasdk
'''

EXAMPLES = '''
- name: Configure NFS as default
  ctera_filer_nfs:
    filer_host: "{{ ctera_filer_hostname }}"
    filer_user: "{{ ctera_filer_user }}"
    filer_password: "{{ ctera_filer_password }}"
'''

RETURN = r''' # '''

from ansible_collections.ctera.ctera.plugins.module_utils.ctera_filer_share_config_base import CteraFilerShareConfigBase

try:
    from cterasdk import gateway_enum
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common


class CteraFilerNfs(CteraFilerShareConfigBase):
    def __init__(self):
        super().__init__(
            dict(
                async_write=dict(type='bool', required=False, default=True),
                aggregate_writes=dict(type='bool', required=False, default=True),
            ),
        )

    @property
    def _share_type(self):
        return "NFS"

    @property
    def _manager(self):
        return self._ctera_filer.nfs

    def _to_config_dict(self, config):
        return dict(
            mode=config.mode,
            async_write=(getattr(config, 'async') == gateway_enum.Mode.Enabled),
            aggregate_writes=(config.aggregateWrites == gateway_enum.Mode.Enabled),
        )


def main():  # pragma: no cover
    CteraFilerNfs().run()


if __name__ == '__main__':  # pragma: no cover
    main()
