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
import munch

import ansible_collections.ctera.ctera.plugins.modules.ctera_filer_smb as ctera_filer_smb
import tests.ut.mocks.ctera_filer_base_mock as ctera_filer_base_mock
from tests.ut.base import BaseTest


class TestCteraFilerSmb(BaseTest):

    def setUp(self):
        super().setUp()
        ctera_filer_base_mock.mock_bases(self, ctera_filer_smb.CteraFilerSmb)

    def test__share_type(self):
        smb = ctera_filer_smb.CteraFilerSmb()
        self.assertEqual(smb._share_type, 'SMB')

    def test__manager(self):
        smb = ctera_filer_smb.CteraFilerSmb()
        self.assertEqual(smb._manager, smb._ctera_filer.smb)

    def test__to_config_dict(self):
        config_dict = dict(
            packet_signing='Disabled',
            idle_disconnect_time=10,
            compatibility_mode=False,
            unix_extensions=True,
            abe_enabled=False
        )
        config_object_dict = copy.deepcopy(config_dict)
        config_object_dict['_classtype'] = 'smb'
        config_object = munch.Munch(config_object_dict)
        smb = ctera_filer_smb.CteraFilerSmb()
        self.assertDictEqual(config_dict, smb._to_config_dict(config_object))
