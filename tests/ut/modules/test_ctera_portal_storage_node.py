# pylint: disable=protected-access

# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is licensed under the Apache License 2.0.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# Copyright 2020, CTERA Networks
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import copy
import unittest.mock as mock
import munch

try:
    from cterasdk import CTERAException, portal_enum, portal_types
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common

import ansible_collections.ctera.ctera.plugins.modules.ctera_portal_storage_node as ctera_portal_storage_node
import tests.ut.mocks.ctera_portal_base_mock as ctera_portal_base_mock
from tests.ut.base import BaseTest


class TestCteraPortalStorageNode(BaseTest):

    def setUp(self):
        super().setUp()
        ctera_portal_base_mock.mock_bases(self, ctera_portal_storage_node.CteraPortalStorageNode)

    def test__execute(self):
        for is_present in [True, False]:
            self._test__execute(is_present)

    @staticmethod
    def _test__execute(is_present):
        storage_node = ctera_portal_storage_node.CteraPortalStorageNode()
        storage_node.parameters = dict(state='present' if is_present else 'absent')
        storage_node._get_storage_node = mock.MagicMock(return_value=dict())
        storage_node._ensure_present = mock.MagicMock()
        storage_node._ensure_absent = mock.MagicMock()
        storage_node._execute()
        if is_present:
            storage_node._ensure_present.assert_called_once_with(mock.ANY)
            storage_node._ensure_absent.assert_not_called()
        else:
            storage_node._ensure_absent.assert_called_once_with(mock.ANY)
            storage_node._ensure_present.assert_not_called()

    def test_get_storage_node_exists(self):
        expected_storage_node_dict = dict(
            name='Example',
            bucket_info=dict(
                bucket_type=portal_enum.BucketType.AWS,
                bucket='ctera_bucket',
                direct=True,
                access_key='ACCESS_KEY',
                secret_key='SECRET',
                endpoint='s3.example.com',
                https=True
            ),
            read_only=True,
            dedicated_to='Main',
        )
        storage_node_obj_dict = copy.deepcopy(expected_storage_node_dict)
        storage_node_obj_dict['readOnly'] = storage_node_obj_dict.pop('read_only')
        storage_node_obj_dict['dedicatedPortal'] = storage_node_obj_dict.pop('dedicated_to')
        storage_node_obj_dict['storage'] = storage_node_obj_dict['bucket_info']['bucket_type']
        storage_node_obj_dict['bucket'] = storage_node_obj_dict['bucket_info']['bucket']
        storage_node_obj_dict['directUpload'] = storage_node_obj_dict['bucket_info']['direct']
        storage_node_obj_dict['awsAccessKey'] = storage_node_obj_dict['bucket_info']['access_key']
        storage_node_obj_dict['awsSecretKey'] = storage_node_obj_dict['bucket_info']['secret_key']
        storage_node_obj_dict['s3Endpoint'] = storage_node_obj_dict['bucket_info']['endpoint']
        storage_node_obj_dict['httpsOnly'] = storage_node_obj_dict['bucket_info']['https']
        storage_node_obj_dict.pop('bucket_info')

        storage_node = ctera_portal_storage_node.CteraPortalStorageNode()
        storage_node.parameters = dict(name=expected_storage_node_dict['name'])
        storage_node._ctera_portal.buckets.get = mock.MagicMock(return_value=munch.Munch(storage_node_obj_dict))
        self.assertDictEqual(expected_storage_node_dict, storage_node._get_storage_node())

    def test__get_storage_node_doesnt_exist(self):
        storage_node = ctera_portal_storage_node.CteraPortalStorageNode()
        storage_node.parameters = dict(name='example')
        storage_node._ctera_portal.buckets.get = mock.MagicMock(side_effect=CTERAException(response=munch.Munch(code=404)))
        self.assertIsNone(storage_node._get_storage_node())

    def test_ensure_present(self):
        for is_present in [True, False]:
            self._test_ensure_present(is_present=is_present)

    @staticmethod
    def _test_ensure_present(is_present):
        storage_node = ctera_portal_storage_node.CteraPortalStorageNode()
        storage_node._handle_create = mock.MagicMock()
        storage_node._handle_modify = mock.MagicMock()
        storage_node._ensure_present({'name': 'example'} if is_present else None)
        if is_present:
            storage_node._handle_modify.assert_called_once_with(mock.ANY)
            storage_node._handle_create.assert_not_called()
        else:
            storage_node._handle_create.assert_called_once_with()
            storage_node._handle_modify.assert_not_called()

    def test__handle_create(self):
        parameters = dict(
            name='Example',
            bucket_info=dict(
                bucket_type=portal_enum.BucketType.AWS,
                bucket='ctera_bucket',
                direct=True,
                access_key='ACCESS_KEY',
                secret_key='SECRET',
                endpoint='s3.example.com',
                https=None
            ),
            read_only=True,
            dedicated_to='Main',
        )
        expected_params = copy.deepcopy(parameters)
        expected_params['bucket'] = mock.ANY
        expected_params.pop('bucket_info')

        storage_node = ctera_portal_storage_node.CteraPortalStorageNode()
        storage_node.parameters = parameters
        storage_node._handle_create()
        storage_node._ctera_portal.buckets.add.assert_called_with(**expected_params)
        self._verify_bucket_info(parameters['bucket_info'], storage_node._ctera_portal.buckets.add.call_args[1]['bucket'])

    def _verify_bucket_info(self, expected_dict, actual_obj):
        self.assertIsInstance(actual_obj, portal_types.AmazonS3)
        self.assertEqual(actual_obj.bucket, expected_dict['bucket'])
        self.assertEqual(actual_obj.driver, expected_dict['bucket_type'])
        self.assertEqual(actual_obj.access_key, expected_dict['access_key'])
        self.assertEqual(actual_obj.secret_key, expected_dict['secret_key'])
        self.assertEqual(actual_obj.endpoint, expected_dict['endpoint'])
        self.assertEqual(actual_obj.https, expected_dict['https'] or True)
        self.assertEqual(actual_obj.direct, expected_dict['direct'])

    def test__handle_modify(self):
        self._test__handle_modify()
        self._test__handle_modify(change_attributes=True)
        self._test__handle_modify(change_attributes=True, change_bucket_info=True)

    @staticmethod
    def _test__handle_modify(change_attributes=False, change_bucket_info=False):
        current_attributes = dict(
            name='Example',
            bucket_info=dict(
                bucket_type=portal_enum.BucketType.AWS,
                bucket='ctera_bucket',
                direct=True,
                access_key='ACCESS_KEY',
                secret_key='SECRET',
                endpoint='s3.example.com',
                https=True
            ),
            read_only=False,
            dedicated_to='Main',
        )
        desired_attributes = copy.deepcopy(current_attributes)
        if change_attributes:
            if change_bucket_info:
                desired_attributes['bucket_info']['https'] = False
            else:
                desired_attributes['read_only'] = True
        storage_node = ctera_portal_storage_node.CteraPortalStorageNode()
        storage_node.parameters = desired_attributes
        storage_node._ensure_present(current_attributes)
        if change_attributes:
            if change_bucket_info:
                storage_node._ctera_portal.buckets.modify.assert_not_called()
            else:
                storage_node._ctera_portal.buckets.modify.assert_called_with(
                    desired_attributes['name'],
                    read_only=desired_attributes['read_only']
                )

    def test_ensure_absent(self):
        for is_present in [True, False]:
            self._test_ensure_absent(is_present)

    @staticmethod
    def _test_ensure_absent(is_present):
        name = 'example'
        storage_node = ctera_portal_storage_node.CteraPortalStorageNode()
        storage_node.parameters = dict(name=name)
        storage_node._ensure_absent(storage_node.parameters if is_present else None)
        if is_present:
            storage_node._ctera_portal.buckets.delete.assert_called_once_with(name)
        else:
            storage_node._ctera_portal.buckets.delete.assert_not_called()

    def test__get_bucket_object_type(self):
        cases = [
            {
                'bucket_type': portal_enum.BucketType.Azure,
                'bucket_object_type': portal_types.AzureBlob
            },
            {
                'bucket_type': portal_enum.BucketType.Scality,
                'bucket_object_type': portal_types.Scality
            },
            {
                'bucket_type': portal_enum.BucketType.AWS,
                'bucket_object_type': portal_types.AmazonS3
            },
            {
                'bucket_type': portal_enum.BucketType.ICOS,
                'bucket_object_type': portal_types.ICOS

            },
            {
                'bucket_type': portal_enum.BucketType.S3Compatible,
                'bucket_object_type': portal_types.S3Compatible
            },
            {
                'bucket_type': portal_enum.BucketType.Nutanix,
                'bucket_object_type': portal_types.Nutanix
            },
            {
                'bucket_type': portal_enum.BucketType.Wasabi,
                'bucket_object_type': portal_types.Wasabi
            },
            {
                'bucket_type': portal_enum.BucketType.Google,
                'bucket_object_type': portal_types.Google
            }
        ]
        for case in cases:
            self.assertEqual(
                ctera_portal_storage_node.CteraPortalStorageNode._get_bucket_object_type(case['bucket_type']),
                case['bucket_object_type']
            )
        self.assertRaises(
            ctera_portal_storage_node.UnsupportedBucketType,
            ctera_portal_storage_node.CteraPortalStorageNode._get_bucket_object_type,
            'Unknown'
        )
