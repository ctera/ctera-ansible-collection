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

import munch

import ansible_collections.ctera.ctera.plugins.modules.ctera_filer_nfs as ctera_filer_nfs
import tests.ut.mocks.ctera_filer_base_mock as ctera_filer_base_mock
from tests.ut.base import BaseTest


class TestCteraFilerNfs(BaseTest):

    def setUp(self):
        super().setUp()
        ctera_filer_base_mock.mock_bases(self, ctera_filer_nfs.CteraFilerNfs)

    def test__share_type(self):
        nfs = ctera_filer_nfs.CteraFilerNfs()
        self.assertEqual(nfs._share_type, 'NFS')

    def test__manager(self):
        nfs = ctera_filer_nfs.CteraFilerNfs()
        self.assertEqual(nfs._manager, nfs._ctera_filer.nfs)

    def test__to_config_dict(self):
        config_dict = dict(
            mode='mode',
            async_write=True,
            aggregate_writes=True
        )
        config_object_dict = dict(
            mode=config_dict['mode'],
            aggregateWrites='enabled'
        )
        config_object_dict['async'] = 'enabled'
        config_object = munch.Munch(config_object_dict)
        nfs = ctera_filer_nfs.CteraFilerNfs()
        self.assertDictEqual(config_dict, nfs._to_config_dict(config_object))
