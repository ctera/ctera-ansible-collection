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

import ansible_collections.ctera.ctera.plugins.modules.ctera_filer_ftp as ctera_filer_ftp
import tests.ut.mocks.ctera_filer_base_mock as ctera_filer_base_mock
from tests.ut.base import BaseTest


class TestCteraFilerFtp(BaseTest):

    def setUp(self):
        super().setUp()
        ctera_filer_base_mock.mock_bases(self, ctera_filer_ftp.CteraFilerFtp)

    def test__share_type(self):
        ftp = ctera_filer_ftp.CteraFilerFtp()
        self.assertEqual(ftp._share_type, 'FTP')

    def test__manager(self):
        ftp = ctera_filer_ftp.CteraFilerFtp()
        self.assertEqual(ftp._manager, ftp._ctera_filer.ftp)

    def test__to_config_dict(self):
        config_dict = dict(
            mode='mode',
            allow_anonymous_ftp=True,
            anonymous_download_limit=1024,
            anonymous_ftp_folder='/tmp',
            banner_message='hello',
            max_connections_per_ip=5,
            require_ssl=True
        )
        config_object = munch.Munch(
            mode=config_dict['mode'],
            AllowAnonymousFTP=config_dict['allow_anonymous_ftp'],
            AnonymousDownloadLimit=config_dict['anonymous_download_limit'],
            AnonymousFTPFolder=config_dict['anonymous_ftp_folder'],
            BannerMessage=config_dict['banner_message'],
            MaxConnectionsPerIP=config_dict['max_connections_per_ip'],
            RequireSSL=config_dict['require_ssl']
        )
        ftp = ctera_filer_ftp.CteraFilerFtp()
        self.assertDictEqual(config_dict, ftp._to_config_dict(config_object))
