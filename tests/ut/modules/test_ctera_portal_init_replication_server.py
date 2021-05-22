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
    from cterasdk import portal_enum
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common


from ansible_collections.ctera.ctera.plugins.modules.ctera_portal_init_replication_server import CteraPortalInitReplication
import tests.ut.mocks.ctera_portal_base_mock as ctera_portal_base_mock
from tests.ut.base import BaseTest


class TestCteraPortalInitReplication(BaseTest):

    def setUp(self):
        super().setUp()
        ctera_portal_base_mock.mock_bases(self, CteraPortalInitReplication)

    def test__execute(self):
        for is_configured in [True, False]:
            self._test__execute(is_configured)

    @staticmethod
    def _test__execute(is_configured):
        init_master = CteraPortalInitReplication()
        init_master._is_already_configured = mock.MagicMock(return_value=is_configured)
        init_master._configure_replication_server = mock.MagicMock()
        init_master._execute()
        if is_configured:
            init_master._configure_replication_server.assert_not_called()
        else:
            init_master._configure_replication_server.assert_called_once_with()

    def test__is_already_configured(self):
        for wizard_state in [v for k, v in portal_enum.SetupWizardStage.__dict__.items() if not k.startswith('_')]:
            self._test__is_already_configured(wizard_state)

    def _test__is_already_configured(self, wizard_state):
        init_master = CteraPortalInitReplication()
        init_master._ctera_portal.setup.get_setup_status = mock.MagicMock(return_value=munch.Munch(dict(wizard=wizard_state)))
        is_configured = init_master._is_already_configured()
        init_master._ctera_portal.setup.get_setup_status.assert_called_once_with()
        self.assertEqual(is_configured, wizard_state == portal_enum.SetupWizardStage.Finish)

    @staticmethod
    def test__configure_replication_server():
        parameters = dict(
            ctera_host="192.168.1.2",
            ipaddr="192.168.1.1",
            secret="BestSecr3tEver",
            replicate_from="server"
        )
        create_params = copy.deepcopy(parameters)
        create_params.pop('ctera_host')
        init_master = CteraPortalInitReplication()
        init_master.parameters = parameters
        init_master._ctera_portal.setup.init_replication_server = mock.MagicMock()
        init_master._configure_replication_server()
        init_master._ctera_portal.setup.init_replication_server.assert_called_once_with(**create_params)
