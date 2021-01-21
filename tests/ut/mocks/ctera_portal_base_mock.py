import unittest.mock as mock

from ansible_collections.ctera.ctera.plugins.module_utils.ctera_common import AnsibleReturnValue
from ansible_collections.ctera.ctera.plugins.module_utils.ctera_runner_base import CteraRunnerBase

class CteraPortalBaseMock(CteraRunnerBase):
    def __init__(self, _argument_spec, **_kwargs):
        self._ctera_portal = mock.MagicMock()
        self._ctera_portal.users = mock.MagicMock()
        self._ctera_portal.users.add = mock.MagicMock()
        self._ctera_portal.users.delete = mock.MagicMock()
        self._ctera_portal.users.get = mock.MagicMock()
        self._ctera_portal.users.list_local_users = mock.MagicMock()
        self._ctera_portal.users.list_domains = mock.MagicMock()
        self._ctera_portal.users.list_domain_users = mock.MagicMock()
        self._ctera_portal.users.modify = mock.MagicMock()

        self.ansible_module = mock.MagicMock()
        self.ansible_return_value = AnsibleReturnValue()
        self.ansible_module.ctera_return_value = mock.MagicMock(return_value=self.ansible_return_value)

    def run(self):
        self._execute()

    def _execute(self):
        pass


def mock_bases(test, klass):
    original_bases = klass.__bases__
    klass.__bases__ = (CteraPortalBaseMock,)
    test.addCleanup(restore_bases, klass, original_bases)


def restore_bases(klass, bases):
    klass.__bases__ = bases
