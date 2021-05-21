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
module: ctera_portal_storage_node
short_description: CTERA-Networks Portal Storage Node Management
description:
    - Manage Portal Storage Node
extends_documentation_fragment:
    - ctera.ctera.vportal

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  state:
    description:
    - Whether the specified Storage Node should exist or not.
    type: str
    choices: ['present', 'absent']
    default: 'present'
  name:
    description: The name of the managed Storage Node
    type: str
    required: True
  bucket_info:
    description: The type of the managed storage node. Required when c(state) is present
    type: dict
    suboptions:
      bucket_type:
        description: The type of the managed storage node
        type: str
        required: True
        choices:
        - Azure
        - Scality
        - AWS
        - ICOS
        - S3Compatible
        - Nutanix
        - Wasabi
        - Google
        - NetAppStorageGRID
      bucket:
        description: Name of the storage node bucket
        type: str
        required: True
      access_key:
        description: Access Key to connect to the bucket
        type: str
        required: True
      secret_key:
        description: Secret Key to connect to the bucket
        type: str
        required: True
      endpoint:
        description: Endpoint of the bucket. Required when c(bucket_type) is ScalityS3, CleverSafeS3, GenericS3 Nutanix WasabiS3 or GoogleS3
        type: str
      https:
        description: Use HTTPS for connection. If not provided, the default per c(bucket_type) is used
        type: bool
      direct:
        description: Use Direct Upload. If not provided, the default per c(bucket_type) is used
        type: bool
  read_only:
    description: Set bucket to read-delete only, defaults to False
    type: bool
    default: False
  dedicated_to:
    description: Name of the tenant to dedicate the storage node to
    type: str
'''

EXAMPLES = '''
- name: New Storage node
  ctera_portal_storage_node:
    name: Example
    bucket_info:
      bucket_type: S3
      bucket: ctera
      access_key: ACCESSKEY
      secret_key: SECRETKEY
    ctera_host: "{{ ctera_portal_hostname }}"
    ctera_user: "{{ ctera_portal_user }}"
    ctera_password: "{{ ctera_portal_password }}"
'''

RETURN = r''' # '''

import copy

try:
    from cterasdk import CTERAException, portal_enum, portal_types
    _VARIABLE_FIELD_NAMES = {
        'access_key': {
            'default': 'awsAccessKey',
            portal_enum.BucketType.Azure: 'accountName'
        },
        'secret_key': {
            'default': 'awsSecretKey',
            portal_enum.BucketType.Azure: 'secretAccess'
        },
        'endpoint': {
            'default': 'endPoint',
            portal_enum.BucketType.AWS: 's3Endpoint'
        },
        'https': {
            'default': 'useHttps',
            portal_enum.BucketType.AWS: 'httpsOnly'
        }
    }
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common

import ansible_collections.ctera.ctera.plugins.module_utils.ctera_common as ctera_common
from ansible_collections.ctera.ctera.plugins.module_utils.ctera_portal_base import CteraPortalBase


class UnsupportedBucketType(Exception):
    pass


class CteraPortalStorageNode(CteraPortalBase):
    _bucket_fields = [
        'name',
        'bucket',
        'storage',
        'endPoint',
        'accountName',
        'secretAccess',
        'useHttps',
        'directUpload',
        'awsAccessKey',
        'awsSecretKey',
        's3Endpoint',
        'httpsOnly',
        'readOnly',
        'dedicatedPortal'
    ]

    _create_params = ['name', 'read_only', 'dedicated_to']

    def __init__(self):
        super().__init__(
            dict(
                state=dict(choices=['present', 'absent'], default='present'),
                name=dict(required=True),
                bucket_info=dict(type='dict', options=dict(
                    bucket_type=dict(required=True, choices=['Azure', 'Scality', 'AWS', 'ICOS',
                                                             'S3Compatible', 'Nutanix', 'Wasabi', 'Google', 'NetAppStorageGRID']),
                    bucket=dict(required=True),
                    access_key=dict(required=True, no_log=True),
                    secret_key=dict(required=True, no_log=True),
                    endpoint=dict(),
                    https=dict(type='bool'),
                    direct=dict(type='bool'),
                )),
                read_only=dict(type='bool', default=False),
                dedicated_to=dict(),
            )
        )

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Storage Node Management failed'

    def _execute(self):
        state = self.parameters.pop('state')
        storage_node = self._get_storage_node()
        if state == 'present':
            self.parameters['bucket_info']['bucket_type'] = portal_enum.BucketType.__dict__[self.parameters['bucket_info']['bucket_type']]
            self._ensure_present(storage_node)
        else:
            self._ensure_absent(storage_node)

    def _ensure_present(self, storage_node):
        if storage_node:
            self._handle_modify(storage_node)
        else:
            self._handle_create()

    def _handle_create(self):
        create_params = {k: v for k, v in self.parameters.items() if k in CteraPortalStorageNode._create_params}
        create_params['bucket'] = self._make_bucket_obj(self.parameters['bucket_info'])
        self._ctera_portal.buckets.add(**create_params)
        self.ansible_module.ctera_return_value().changed().msg('Storage Node was created')

    @staticmethod
    def _make_bucket_obj(bucket_dict):
        return CteraPortalStorageNode._get_bucket_object_type(bucket_dict['bucket_type'])(**CteraPortalStorageNode._get_bucket_params(bucket_dict))

    @staticmethod
    def _get_bucket_params(bucket_dict):
        bucket_params = copy.deepcopy(bucket_dict)
        bucket_params.pop('bucket_type')
        params_with_default = ['https', 'direct']
        if bucket_dict['bucket_type'] in [portal_enum.BucketType.Azure, portal_enum.BucketType.AWS]:
            params_with_default.append('endpoint')
        for param in params_with_default:
            if bucket_params[param] is None:
                bucket_params.pop(param)
        return bucket_params

    @staticmethod
    def _get_bucket_object_type(bucket_type):
        bucket_object_type = None
        if bucket_type == portal_enum.BucketType.Azure:
            bucket_object_type = portal_types.AzureBlob
        elif bucket_type == portal_enum.BucketType.Scality:
            bucket_object_type = portal_types.Scality
        elif bucket_type == portal_enum.BucketType.AWS:
            bucket_object_type = portal_types.AmazonS3
        elif bucket_type == portal_enum.BucketType.ICOS:
            bucket_object_type = portal_types.ICOS
        elif bucket_type == portal_enum.BucketType.S3Compatible:
            bucket_object_type = portal_types.S3Compatible
        elif bucket_type == portal_enum.BucketType.Nutanix:
            bucket_object_type = portal_types.Nutanix
        elif bucket_type == portal_enum.BucketType.Wasabi:
            bucket_object_type = portal_types.Wasabi
        elif bucket_type == portal_enum.BucketType.Google:
            bucket_object_type = portal_types.Google
        elif bucket_type == portal_enum.BucketType.NetAppStorageGRID:
            bucket_object_type = portal_types.NetAppStorageGRID
        else:
            raise UnsupportedBucketType("Provided bucket type is not supported %s" % bucket_type)
        return bucket_object_type

    def _handle_modify(self, storage_node):
        messages = []
        changed = False

        modified_attributes = ctera_common.get_modified_attributes(storage_node, self.parameters)
        if 'bucket_info' in modified_attributes:
            messages.append("Modifying the bucket info is currently not supported")
            modified_attributes.pop('bucket_info')

        if modified_attributes:
            self._ctera_portal.buckets.modify(self.parameters['name'], **modified_attributes)
            changed = True
            messages.append('Storage Node was modified')
        else:
            messages.append('Storage Node details did not change')

        if changed:
            self.ansible_module.ctera_return_value().changed()
        else:
            self.ansible_module.ctera_return_value().skipped()
        self.ansible_module.ctera_return_value().put(name=self.parameters['name']).msg(' '.join(messages))

    def _ensure_absent(self, storage_node):
        if storage_node:
            self._ctera_portal.buckets.delete(self.parameters['name'])
            self.ansible_module.ctera_return_value().changed().msg('Storage Node deleted').put(name=self.parameters['name'])
        else:
            self.ansible_module.ctera_return_value().skipped().msg('Storage Node already does not exist').put(name=self.parameters['name'])

    def _get_storage_node(self):
        storage_node = None
        try:
            storage_node = self._ctera_portal.buckets.get(self.parameters['name'], include=CteraPortalStorageNode._bucket_fields)
        except CTERAException:
            pass
        return self._to_storage_node_dict(storage_node) if storage_node else None

    @staticmethod
    def _to_storage_node_dict(storage_node_obj):
        return {
            'name': storage_node_obj.name,
            'bucket_info': CteraPortalStorageNode._get_bucket_info(storage_node_obj),
            'read_only': storage_node_obj.readOnly,
            'dedicated_to': storage_node_obj.dedicatedPortal
        }

    @staticmethod
    def _get_bucket_info(storage_node_obj):
        bucket_info_dict = {
            field: getattr(
                storage_node_obj,
                _VARIABLE_FIELD_NAMES[field].get(storage_node_obj.storage, _VARIABLE_FIELD_NAMES[field]['default'])
            ) for field in _VARIABLE_FIELD_NAMES
        }
        bucket_info_dict.update(
            {
                'bucket_type': storage_node_obj.storage,
                'bucket': storage_node_obj.bucket,
                'direct': storage_node_obj.directUpload
            }
        )
        return bucket_info_dict


def main():  # pragma: no cover
    CteraPortalStorageNode().run()


if __name__ == '__main__':  # pragma: no cover
    main()
