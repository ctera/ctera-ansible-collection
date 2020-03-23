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

import ansible_collections.ctera.ctera.plugins.modules.ctera_filer_async_io as ctera_filer_async_io
import tests.ut.mocks.ctera_filer_base_mock as ctera_filer_base_mock
from tests.ut.base import BaseTest


class TestCteraFilerAsyncIO(BaseTest):

    def setUp(self):
        super().setUp()
        ctera_filer_base_mock.mock_bases(self, ctera_filer_async_io.CteraFilerAsyncIO)

    def test__execute(self):
        for current in [True, False]:
            for desired in [True, False]:
                self._test__execute(current, desired)

    def _test__execute(self, current, desired):
        async_io = ctera_filer_async_io.CteraFilerAsyncIO()
        async_io.parameters = dict(enabled=desired)
        async_io._ctera_filer.aio.is_enabled.return_value = current  # pylint: disable=protected-access
        async_io.run()
        if current == desired:
            async_io._ctera_filer.aio.enable.assert_not_called()  # pylint: disable=protected-access
            async_io._ctera_filer.aio.disable.assert_not_called()  # pylint: disable=protected-access
            self.assertFalse(hasattr(async_io.ansible_return_value.param, 'changed'))
            self.assertEqual(async_io.ansible_return_value.param.msg, 'asynchronous I/O is already %sabled' % ('en' if desired else 'dis'))
        else:
            if desired:
                async_io._ctera_filer.aio.enable.assert_called_once_with()  # pylint: disable=protected-access
                async_io._ctera_filer.aio.disable.assert_not_called()  # pylint: disable=protected-access

            else:
                async_io._ctera_filer.aio.disable.assert_called_once_with()  # pylint: disable=protected-access
                async_io._ctera_filer.aio.enable.assert_not_called()  # pylint: disable=protected-access
            self.assertTrue(async_io.ansible_return_value.param.changed)
            self.assertEqual(async_io.ansible_return_value.param.msg, '%sabled asynchronous I/O' % ('En' if desired else 'Dis'))
