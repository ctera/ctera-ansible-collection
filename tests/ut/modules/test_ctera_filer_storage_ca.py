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
    from cterasdk import Object
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common

import ansible_collections.ctera.ctera.plugins.modules.ctera_filer_storage_ca as ctera_filer_storage_ca
import tests.ut.mocks.ctera_filer_base_mock as ctera_filer_base_mock
from tests.ut.base import BaseTest


class TestCteraFilerStorageCA(BaseTest):

    def setUp(self):
        super().setUp()
        self._certificate = 'certificate'
        self._issuer = 'issuer'
        self._subject = 'subject'
        ctera_filer_base_mock.mock_bases(self, ctera_filer_storage_ca.CteraFilerStorageCA)

    def test_import_certificate_no_match_issuer_no_force(self):
        self._test_import_certificate('random', self._subject, False)

    def test_import_certificate_no_match_issuer_no_force(self):
        self._test_import_certificate(self._issuer, 'random', False)

    def test_import_certificate_match_force(self):
        self._test_import_certificate(self._issuer, self._subject, True)

    def test_match_no_update_no_force(self):
        self._test_import_certificate(self._issuer, self._subject, False)

    def _test_import_certificate(self, issuer, subject, force_update):
        ssl = ctera_filer_storage_ca.CteraFilerStorageCA()
        mock_load_certificate = mock.patch("cterasdk.lib.crypto.X509Certificate.load_certificate").start()
        certificate = Object()
        certificate.issuer = issuer
        certificate.subject = subject
        mock_load_certificate.return_value = certificate
        ssl.parameters = dict(
            certificate=self._certificate,
            force_update=force_update
        )
        ssl._ctera_filer.ssl.get_storage_ca = mock.MagicMock(
            return_value=TestCteraFilerStorageCA._get_storage_ca_response(self._issuer, self._subject)
        )
        ssl._ctera_filer.ssl.import_storage_ca = mock.MagicMock()
        ssl._execute()
        if force_update or issuer not in self._issuer or subject not in self._subject:
            ssl._ctera_filer.ssl.import_storage_ca.assert_called_once_with(self._certificate)
        else:
            ssl._ctera_filer.ssl.import_storage_ca.assert_not_called()

    @staticmethod
    def _get_storage_ca_response(issuerName, subjectName):
        param = Object()
        param.issuerName = issuerName
        param.subjectName = subjectName
        return param
