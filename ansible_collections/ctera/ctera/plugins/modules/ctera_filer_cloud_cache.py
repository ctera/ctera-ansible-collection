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
module: ctera_filer_cloud_cache
short_description: CTERA-Networks Filer Cloud Sync configuration and management
description:
    - Enable or Disable Cloud-Sync
    - Refresh folders
version_added: "2.10"
extends_documentation_fragment:
    - ctera.ctera.filer

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  enabled:
    description:
    - Whether Cloud Cache should be enabled or disabled
    type: bool
    default: True
  sync_enabled:
    description:
    - Whether Cloud Sync should be enabled or disabled
    type: bool
    default: True
  force_eviction:
    description:
    - Force the execution of the file eviction process
    type: bool
    default: False
  refresh_folders:
    description:
    - Whether to execute refresh folders
    type: bool
    default: False
'''

EXAMPLES = '''
- name: Enable Caching Gateway and start sync w/o refresh
  ctera_filer_cloud_sync:
    filer_host: "{{ ctera_filer_hostname }}"
    filer_user: "{{ ctera_filer_user }}"
    filer_password: "{{ ctera_filer_password }}"

- name: Enable Caching Gateway and start sync with refresh
  ctera_filer_cloud_sync:
    refresh_folders: True
    filer_host: "{{ ctera_filer_hostname }}"
    filer_user: "{{ ctera_filer_user }}"
    filer_password: "{{ ctera_filer_password }}"

- name: Enable Caching Gateway w/o sync
  ctera_filer_cloud_sync:
    sync_enabled: False
    filer_host: "{{ ctera_filer_hostname }}"
    filer_user: "{{ ctera_filer_user }}"
    filer_password: "{{ ctera_filer_password }}"

- name: Disable Caching Gateway
  ctera_filer_cloud_sync:
    enabled: False
    filer_host: "{{ ctera_filer_hostname }}"
    filer_user: "{{ ctera_filer_user }}"
    filer_password: "{{ ctera_filer_password }}"
'''

RETURN = r''' # '''

import ansible_collections.ctera.ctera.plugins.module_utils.ctera_common as ctera_common
from ansible_collections.ctera.ctera.plugins.module_utils.ctera_filer_base import CteraFilerBase


class CteraFilerCloudSync(CteraFilerBase):
    def __init__(self):
        super().__init__(dict(
            enabled=dict(type='bool', required=False, default=True),
            sync_enabled=dict(type='bool', required=False, default=True),
            force_eviction=dict(type='bool', required=False, default=False),
            refresh_folders=dict(type='bool', required=False, default=False),
        ))

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Cloud Cache management failed'

    def _execute(self):
        if not self._ctera_filer.services.connected():
            self._handle_not_connected()
            return

        is_cache_enabled = self._ctera_filer.cache.is_enabled()
        if self.parameters['enabled']:
            self._ensure_cache_enabled(is_cache_enabled)
        else:
            self._ensure_cache_disabled(is_cache_enabled)

    def _ensure_cache_enabled(self, is_cache_enabled):
        messages = {
            'skipped': [],
            'changed': []
        }
        if is_cache_enabled:
            messages['skipped'].append('Cloud cache was already enabled')
        else:
            self._ctera_filer.cache.enable()
            messages['changed'].append('Cloud cache was enabled')

        if self.parameters['force_eviction']:
            self._ctera_filer.cache.force_eviction()
            messages['changed'].append('Started force file eviction')

        is_sync_enabled = self._ctera_filer.sync.is_enabled()
        if self.parameters['sync_enabled']:
            self._ensure_sync_enabled(is_sync_enabled, messages)
        else:
            self._ensure_sync_disabled(is_sync_enabled, messages)

        ctera_common.set_result(self.ansible_module, messages)

    def _ensure_cache_disabled(self, is_cache_enabled):
        if is_cache_enabled:
            self._ctera_filer.cache.disable()
            self.ansible_module.ctera_return_value().changed().msg('Cloud cache was disabled')
        else:
            self.ansible_module.ctera_return_value().skipped().msg('Cloud cache is already disabled')

    def _ensure_sync_enabled(self, is_sync_enabled, messages):
        if is_sync_enabled:
            messages['skipped'].append('Cloud sync was already enabled')
        else:
            if len(self._ctera_filer.volumes.get()) == 0:
                messages['skipped'].append('No volumes defined - cannot enabled sync')
                return
            self._ctera_filer.sync.unsuspend()
            messages['changed'].append('Cloud sync was enabled')

        if self.parameters['refresh_folders']:
            self._ctera_filer.sync.refresh()
            messages['changed'].append('Started refreshing cloud folders')

    def _ensure_sync_disabled(self, is_sync_enabled, messages):
        if is_sync_enabled:
            self._ctera_filer.sync.suspend()
            messages['changed'].append('Cloud sync was disabled')
        else:
            messages['skipped'].append('Cloud sync was already disabled')

    def _handle_not_connected(self):
        self.ansible_module.ctera_return_value().msg('Filer is not connected to Cloud Services')
        if self.parameters['enabled']:
            self.ansible_module.ctera_return_value().failed()
        else:
            self.ansible_module.ctera_return_value().skipped()


def main():  # pragma: no cover
    CteraFilerCloudSync().run()


if __name__ == '__main__':  # pragma: no cover
    main()
