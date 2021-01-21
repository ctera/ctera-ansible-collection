import unittest.mock as mock

from ansible_collections.ctera.ctera.plugins.module_utils.ctera_common import AnsibleReturnValue
from ansible_collections.ctera.ctera.plugins.module_utils.ctera_runner_base import CteraRunnerBase

class CteraFilerBaseMock(CteraRunnerBase):
    def __init__(self, _argument_spec, **_kwargs):
        self._ctera_filer = mock.MagicMock()
        self._ctera_filer.aio = mock.MagicMock()
        self._ctera_filer.aio.enable = mock.MagicMock()
        self._ctera_filer.aio.disable = mock.MagicMock()
        self._ctera_filer.backup = mock.MagicMock()
        self._ctera_filer.backup.configure = mock.MagicMock()
        self._ctera_filer.cache = mock.MagicMock()
        self._ctera_filer.cache.disable = mock.MagicMock()
        self._ctera_filer.cache.enable = mock.MagicMock()
        self._ctera_filer.cache.force_eviction = mock.MagicMock()
        self._ctera_filer.config = mock.MagicMock()
        self._ctera_filer.config.set_hostname = mock.MagicMock()
        self._ctera_filer.config.set_location = mock.MagicMock()
        self._ctera_filer.config.enbale_wizard = mock.MagicMock()
        self._ctera_filer.config.disbale_wizard = mock.MagicMock()
        self._ctera_filer.directoryservice = mock.MagicMock()
        self._ctera_filer.directoryservice.connect = mock.MagicMock()
        self._ctera_filer.directoryservice.disconnect = mock.MagicMock()
        self._ctera_filer.ftp = mock.MagicMock()
        self._ctera_filer.licenses = mock.MagicMock()
        self._ctera_filer.licenses.apply = mock.MagicMock()
        self._ctera_filer.network = mock.MagicMock()
        self._ctera_filer.network.enable_dhcp = mock.MagicMock()
        self._ctera_filer.network.set_static_nameserver = mock.MagicMock()
        self._ctera_filer.network.set_static_ipaddr = mock.MagicMock()
        self._ctera_filer.power = mock.MagicMock()
        self._ctera_filer.power.reboot = mock.MagicMock()
        self._ctera_filer.power.reset = mock.MagicMock()
        self._ctera_filer.services = mock.MagicMock()
        self._ctera_filer.services.connect = mock.MagicMock()
        self._ctera_filer.services.disconnect = mock.MagicMock()
        self._ctera_filer.services.disable_sso = mock.MagicMock()
        self._ctera_filer.services.enable_sso = mock.MagicMock()
        self._ctera_filer.services.reconnect = mock.MagicMock()
        self._ctera_filer.shares = mock.MagicMock()
        self._ctera_filer.shares.add = mock.MagicMock()
        self._ctera_filer.shares.delete = mock.MagicMock()
        self._ctera_filer.shares.modify = mock.MagicMock()
        self._ctera_filer.sync = mock.MagicMock()
        self._ctera_filer.sync.refresh = mock.MagicMock()
        self._ctera_filer.sync.suspend = mock.MagicMock()
        self._ctera_filer.sync.unsuspend = mock.MagicMock()
        self._ctera_filer.syslog = mock.MagicMock()
        self._ctera_filer.syslog.enable = mock.MagicMock()
        self._ctera_filer.syslog.modify = mock.MagicMock()
        self._ctera_filer.syslog.disable = mock.MagicMock()
        self._ctera_filer.telnet = mock.MagicMock()
        self._ctera_filer.telnet.enable = mock.MagicMock()
        self._ctera_filer.telnet.disable = mock.MagicMock()
        self._ctera_filer.timezone = mock.MagicMock()
        self._ctera_filer.timezone.set_timezone = mock.MagicMock()
        self._ctera_filer.users = mock.MagicMock()
        self._ctera_filer.users.add = mock.MagicMock()
        self._ctera_filer.users.add_first_user = mock.MagicMock()
        self._ctera_filer.users.delete = mock.MagicMock()
        self._ctera_filer.users.modify = mock.MagicMock()
        self._ctera_filer.volumes = mock.MagicMock()
        self._ctera_filer.volumes.add = mock.MagicMock()
        self._ctera_filer.volumes.delete = mock.MagicMock()
        self._ctera_filer.volumes.modify = mock.MagicMock()
        self._ctera_filer.share_mock = mock.MagicMock()
        self._ctera_filer.share_mock.enable = mock.MagicMock()
        self._ctera_filer.share_mock.disable = mock.MagicMock()
        self._ctera_filer.share_mock.modify = mock.MagicMock()
        self.ansible_module = mock.MagicMock()
        self.ansible_return_value = AnsibleReturnValue()
        self.ansible_module.ctera_return_value = mock.MagicMock(return_value=self.ansible_return_value)

    def run(self):
        self._execute()

    def _execute(self):
        pass


def mock_bases(test, klass):
    original_bases = klass.__bases__
    klass.__bases__ = (CteraFilerBaseMock,)
    test.addCleanup(restore_bases, klass, original_bases)


def restore_bases(klass, bases):
    klass.__bases__ = bases
