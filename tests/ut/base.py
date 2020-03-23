from __future__ import (absolute_import, division, print_function)

from unittest import TestCase
import unittest.mock as mock


class BaseTest(TestCase):

    def patch_call(self, module_path, **patch_kwargs):
        """Mock patch a given path as a call and schedule proper mock cleanup."""
        call_patcher = mock.patch(module_path, **patch_kwargs)
        self.addCleanup(call_patcher.stop)
        return call_patcher.start()
