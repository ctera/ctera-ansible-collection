try:
    from cterasdk import CTERAException
except ImportError:  # pragma: no cover
    pass

from ansible_collections.ctera.ctera.plugins.module_utils import ctera_filer_base
from tests.ut.mocks.gateway_ansible_module_mock import mock_gateway_ansible_module
from tests.ut.base import BaseTest


class CteraFilerTestChild(ctera_filer_base.CteraFilerBase):

    def __init__(self, success):
        super().__init__({})
        self._success = success
        self.execute_called = False
        self.generic_failure_message_called = False

    @property
    def _generic_failure_message(self):
        self.generic_failure_message_called = True
        return "Test Child"

    def _execute(self):
        self.execute_called = True
        if not self._success:
            raise CTERAException("Testing Failure")

class TestCteraFilerBase(BaseTest):  #pylint: disable=too-many-public-methods

    def setUp(self):
        super().setUp()
        self._obj_mock = mock_gateway_ansible_module(self, "ansible_collections.ctera.ctera.plugins.module_utils.ctera_filer_base.GatewayAnsibleModule")

    def test_run_success(self):
        runner = CteraFilerTestChild(True)
        runner.run()
        self._obj_mock.ctera_filer.assert_called_once_with(login=True)
        self.assertTrue(runner.execute_called)
        self.assertFalse(runner.generic_failure_message_called)
        self._obj_mock.ctera_logout.assert_called_once_with()
        self._obj_mock.ctera_exit.assert_called_once_with()

    def test_run_failure(self):
        runner = CteraFilerTestChild(False)
        runner.run()
        self._obj_mock.ctera_filer.assert_called_once_with(login=True)
        self.assertTrue(runner.execute_called)
        self.assertTrue(runner.generic_failure_message_called)
        self._obj_mock.ctera_logout.assert_called_once_with()
        self._obj_mock.ctera_exit.assert_called_once_with()
