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
    from cterasdk import CTERAException, Object
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common

import ansible_collections.ctera.ctera.plugins.modules.ctera_portal_certificate as ctera_portal_certificate
import tests.ut.mocks.ctera_portal_base_mock as ctera_portal_base_mock
from tests.ut.base import BaseTest


class TestCteraPortalCertificate(BaseTest):

    def setUp(self):
        super().setUp()
        self._private_key = 'key'
        self._domain_cert = 'domain_cert'
        self._intermediate = 'intermediate'
        self._root = 'root'
        self._thumbprint = 'thumbprint'
        ctera_portal_base_mock.mock_bases(self, ctera_portal_certificate.CteraPortalCertificate)

    def test_import_certificate_no_match_no_force(self):
        self._test_import_certificate('random', False)

    def test_import_certificate_match_force(self):
        self._test_import_certificate(self._thumbprint, True)

    def test_match_no_update(self):
        self._test_import_certificate(self._thumbprint, False)

    def _test_import_certificate(self, sha1_fingerprint, force_update):
        ssl = ctera_portal_certificate.CteraPortalCertificate()
        mock_load_certificate = mock.patch("cterasdk.lib.crypto.X509Certificate.load_certificate").start()
        certificate = Object()
        certificate.sha1_fingerprint = sha1_fingerprint
        mock_load_certificate.return_value = certificate
        ssl.parameters = dict(
            private_key=self._private_key,
            server_certificate=self._domain_cert,
            certificate_chain=[self._intermediate, self._root],
            force_update=force_update
        )
        ssl._ctera_portal.ssl.thumbprint = self._thumbprint
        ssl._ctera_portal.ssl.import_from_chain = mock.MagicMock()
        ssl._execute()
        if force_update or sha1_fingerprint != self._thumbprint:
            ssl._ctera_portal.ssl.import_from_chain.assert_called_once_with(self._private_key, *[self._domain_cert, self._intermediate, self._root])
        else:
            ssl._ctera_portal.ssl.import_from_chain.assert_not_called()
