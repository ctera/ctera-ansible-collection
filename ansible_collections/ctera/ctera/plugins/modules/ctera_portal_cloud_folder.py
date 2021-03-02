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
module: ctera_portal_cloud_folder
short_description: CTERA-Networks Portal cloud folder configuration and management
description:
    - Create, and delete cloud folders.
extends_documentation_fragment:
    - ctera.ctera.vportal

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  state:
    description:
    - Whether the specified user should exist or not.
    type: str
    choices: ['present', 'absent']
    default: 'present'
  name:
    description: The name of the cloud folder
    required: True
    type: str
  group:
    description: The folder group to which the cloud folder belongs
    type: str
  owner:
    description: The cloud folder owner
    type: dict
    required: True
    suboptions:
      name:
        description: The user name
        required: True
        type: str
      directory:
        description: The fully-qualified name of the user directory, if the user belongs to one
        type: str
  winacls:
    description: Use Windows ACLs
    type: bool
    default: True

'''

EXAMPLES = '''
- name: Cloud Folder
  ctera_portal_cloud_folder:
    name: "AliceFiles"
    group: "CompanyMain"
    owner:
      name: "Alice"
    ctera_host: "{{ ctera_portal_hostname }}"
    ctera_user: "{{ ctera_portal_user }}"
    ctera_password: "{{ ctera_portal_password }}"

'''

RETURN = '''
name:
  description: Name of the cloud folder
  returned: when state is present
  type: str
  sample: CompanyMain
'''

from ansible_collections.ctera.ctera.plugins.module_utils.ctera_portal_base import CteraPortalBase

try:
    from cterasdk import CTERAException, portal_types
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common


class CteraPortalCloudFolder(CteraPortalBase):
    def __init__(self):
        super().__init__(
            dict(
                state=dict(required=False, choices=['present', 'absent'], default='present'),
                name=dict(type='str', required=True),
                group=dict(type='str'),
                owner=dict(
                    type='dict',
                    required=True,
                    options=dict(
                        name=dict(type='str', required=True),
                        directory=dict(type='str')
                    )
                ),
                winacls=dict(type='bool', default=True)
            ),
            required_if=[('state', 'present', ['group', 'winacls'])]
        )

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Cloud Folder management failed'

    def _execute(self):
        state = self.parameters.pop('state')
        cloud_folder = self._get_cloud_folder()
        if state == 'present':
            self._ensure_present(cloud_folder)
        else:
            self._ensure_absent(cloud_folder)

    def _get_cloud_folder(self):
        cloud_folder = None
        try:
            cloud_folder = self._ctera_portal.cloudfs.find(
                self.parameters['name'],
                self._make_user_account(self.parameters['owner']),
                ['name', 'group', 'owner']
            )
        except CTERAException:
            pass
        return self._to_cloud_folder_dict(cloud_folder) if cloud_folder else None

    @staticmethod
    def _to_cloud_folder_dict(cloud_folder):
        return dict(
            name=cloud_folder.name,
            group=cloud_folder.group.split('/')[-1],
            owner=dict(name=cloud_folder.owner.split('/')[-1])
        )

    def _ensure_present(self, cloud_folder):
        if cloud_folder:
            self.ansible_module.ctera_return_value().skipped().msg('Cloud Folder already exists').put(name=self.parameters['name'])
        else:
            self._ctera_portal.cloudfs.mkdir(
                self.parameters['name'],
                self.parameters['group'],
                self._make_user_account(self.parameters['owner']),
                winacls=self.parameters['winacls']
            )
            self.ansible_module.ctera_return_value().changed().msg('Cloud Folder created').put(name=self.parameters['name'])

    def _ensure_absent(self, cloud_folder):
        if cloud_folder:
            self._ctera_portal.cloudfs.delete(self.parameters['name'], self._make_user_account(self.parameters['owner']))
            self.ansible_module.ctera_return_value().changed().msg('Cloud Folder deleted').put(name=self.parameters['name'])
        else:
            self.ansible_module.ctera_return_value().skipped().msg('Cloud Folder already does not exist').put(name=self.parameters['name'])

    @staticmethod
    def _make_user_account(user_details):
        return portal_types.UserAccount(**user_details) if user_details else None


def main():  # pragma: no cover
    CteraPortalCloudFolder().run()


if __name__ == '__main__':  # pragma: no cover
    main()
