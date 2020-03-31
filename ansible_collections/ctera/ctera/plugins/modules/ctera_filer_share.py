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
module: ctera_filer_share
short_description: CTERA Filer share configuration and management
description:
    - Create, modify and delete shares.
    - This module does not handle the creation of the directory and share creation will fail if the directory does not exist
version_added: "2.10"
extends_documentation_fragment:
    - ctera.ctera.filer

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  state:
    description:
    - Whether the specified share should exist or not.
    type: str
    choices: ['present', 'absent']
    default: 'present'
  name:
    description: The name of the share
    required: True
    type: str
  directory:
    description:
    - The directory to share
    - Required when C(state=present) and the share does not exist
    type: str
  acl:
    description: List of Access Control Entries
    type: list
    suboptions:
      principal_type:
        description: The principal type
        type: str
        choices:
        - LocalUser
        - LocalGroup
        - DomainUser
        - DomainGroup
        required: True
      name:
        description: The name of the user or group
        type: str
        required: True
      perm:
        description: The file access permission
        type: str
        choices:
        - ReadWrite
        - ReadOnly
        - None
        required: True
  access:
    description: The Windows File Sharing authentication mode
    type: str
    choices:
    - winAclMode
    - authenticated
    default: winAclMode
  csc:
    description: The client side caching (offline files) configuration
    type: str
    choices:
    - manual
    - documents
    - disabled
    default: manual
  dir_permissions:
    description: Directory Permission
    type: int
    default: 777
  export_to_afp:
    description: Export the share to AFP
    type: bool
    default: False
  export_to_ftp:
    description: Export the share to FTP
    type: bool
    default: False
  export_to_nfs:
    description: Export the share to NFS
    type: bool
    default: False
  export_to_pc_agent:
    description: Export the share to PC Agent
    type: bool
    default: False
  export_to_rsync:
    description: Export the share to RSync
    type: bool
    default: False
  indexed:
    description: Enabled indexing
    type: bool
    default: False
  comment:
    description: Comment
    type: str
'''

EXAMPLES = '''
- name: create local share
  ctera_filer_share:
    name: demo
    directory: /main/public/demo
    acl:
      name: Everyone
      type: LocalGroup
      perm: ReadWrite
    access: authenticated
    filer_host: "{{ ctera_filer_hostname }}"
    filer_user: "{{ ctera_filer_user }}"
    filer_password: "{{ ctera_filer_password }}"
'''

RETURN = '''
name:
  description: The name of the managed share
  returned: Always
  type: str
  sample: demo
'''


import os

import ansible_collections.ctera.ctera.plugins.module_utils.ctera_common as ctera_common
from ansible_collections.ctera.ctera.plugins.module_utils.ctera_filer_base import CteraFilerBase

try:
    from cterasdk import CTERAException, gateway_enum, gateway_types
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common


class CteraFilerShare(CteraFilerBase):
    _add_params = [
        'name',
        'directory',
        'acl',
        'access',
        'csc',
        'dir_permissions',
        'comment',
        'export_to_afp',
        'export_to_ftp',
        'export_to_nfs',
        'export_to_pc_agent',
        'export_to_rsync',
        'indexed'
    ]

    def __init__(self):
        super().__init__(dict(
            state=dict(required=False, choices=['present', 'absent'], default='present'),
            name=dict(type='str', required=True),
            directory=dict(type='str', required=False),
            acl=dict(
                type='list',
                required=False,
                elements='dict',
                options=dict(
                    principal_type=dict(required=True, choices=['LocalUser', 'LocalGroup', 'DomainUser', 'DomainGroup']),
                    name=dict(required=True),
                    perm=dict(required=True, choices=['ReadWrite', 'ReadOnly', 'None']),
                )
            ),
            access=dict(required=False, choices=['winAclMode', 'authenticated'], default='winAclMode'),
            csc=dict(required=False, choices=['manual', 'documents', 'disabled'], default='manual'),
            dir_permissions=dict(required=False, type='int', default=777),
            comment=dict(type='str', required=False),
            export_to_afp=dict(type='bool', required=False, default=False),
            export_to_ftp=dict(type='bool', required=False, default=False),
            export_to_nfs=dict(type='bool', required=False, default=False),
            export_to_pc_agent=dict(type='bool', required=False, default=False),
            export_to_rsync=dict(type='bool', required=False, default=False),
            indexed=dict(type='bool', required=False, default=False)
        ))

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Share management failed'

    def _execute(self):
        state = self.parameters.pop('state')
        share = self._get_share()
        if state == 'present':
            self._ensure_present(share)
        else:
            self._ensure_absent(share)

    def _get_share(self):
        share = None
        try:
            share = self._ctera_filer.shares.get(name=self.parameters['name'])
        except CTERAException as error:
            if error.response.code != 404:  # pylint: disable=no-member
                raise
        return self._to_share_dict(share) if share else None

    def _ensure_present(self, share):
        if share:
            self._handle_modify(share)
        else:
            self._add_share()

    def _add_share(self):
        add_params = {k: v for k, v in self.parameters.items() if k in CteraFilerShare._add_params}
        if add_params.get('directory') is None:
            raise CTERAException(message="Cannot create new share without a directory")
        if add_params.get('acl') is not None:
            add_params['acl'] = [self._make_ShareAccessControlEntry(acl_entry) for acl_entry in add_params['acl']]
        self._ctera_filer.shares.add(**add_params)
        self.ansible_module.ctera_return_value().changed().msg('Share created').put(name=self.parameters['name'])

    def _handle_modify(self, share):
        modified_attributes = ctera_common.get_modified_attributes(share, self.parameters)
        if modified_attributes:
            acl_changes = modified_attributes.get('acl')
            if acl_changes is not None:
                modified_attributes['acl'] = [self._make_ShareAccessControlEntry(acl_entry) for acl_entry in acl_changes]
            self._ctera_filer.shares.modify(self.parameters['name'], **modified_attributes)
            self.ansible_module.ctera_return_value().changed().msg('Share modified').put(name=self.parameters['name'])
        else:
            self.ansible_module.ctera_return_value().skipped().msg('Share details did not change').put(name=self.parameters['name'])

    def _ensure_absent(self, share):
        if share:
            self._ctera_filer.shares.delete(self.parameters['name'])
            self.ansible_module.ctera_return_value().changed().msg('Share deleted').put(name=self.parameters['name'])
        else:
            self.ansible_module.ctera_return_value().skipped().msg('Share does not exist').put(name=self.parameters['name'])

    @staticmethod
    def _make_ShareAccessControlEntry(acl_dict):
        return gateway_types.ShareAccessControlEntry(principal_type=acl_dict['principal_type'], name=acl_dict['name'], perm=acl_dict['perm'])

    @staticmethod
    def _to_share_dict(share_obj):
        share_dict = {}
        share_dict['name'] = share_obj.name
        share_dict['directory'] = os.path.join(share_obj.volume, share_obj.directory[1:])
        share_dict['acl'] = [CteraFilerShare._to_acl_dict(acl_entry) for acl_entry in share_obj.acl]
        share_dict['access'] = share_obj.access
        share_dict['csc'] = share_obj.clientSideCaching
        share_dict['dir_permissions'] = share_obj.dirPermissions
        share_dict['comment'] = share_obj.comment
        share_dict['export_to_afp'] = share_obj.exportToAFP
        share_dict['export_to_ftp'] = share_obj.exportToFTP
        share_dict['export_to_nfs'] = share_obj.exportToNFS
        share_dict['export_to_pc_agent'] = share_obj.exportToPCAgent
        share_dict['export_to_rsync'] = share_obj.exportToRSync
        share_dict['indexed'] = share_obj.indexed
        return share_dict

    @staticmethod
    def _to_acl_dict(acl_obj):
        acl_dict = {}
        acl_dict['perm'] = acl_obj.permissions.allowedFileAccess
        acl_dict['principal_type'] = acl_obj.principal2._classname  # pylint: disable=protected-access
        if acl_dict['principal_type'] in [gateway_enum.PrincipalType.LU, gateway_enum.PrincipalType.LG]:
            name = acl_obj.principal2.ref
            name = name[name.rfind('#') + 1:]
        else:
            name = acl_obj.principal2.name
        acl_dict['name'] = name
        return acl_dict


def main():  # pragma: no cover
    CteraFilerShare().run()


if __name__ == '__main__':  # pragma: no cover
    main()
