filer_trust_certificate = False

class AnsibleModuleMock():

    def __init__(self, _argument_spec, **_kwargs):
        self.params = dict(
            filer_host='192.168.1.1',
            filer_user='admin',
            filer_https=True,
            filer_port=None,
            filer_password='password',
            filer_trust_certificate=filer_trust_certificate
        )
        self.fail_dict = {}
        self.exit_dict = {}

    def fail_json(self, **kwargs):
        for k, v in kwargs.items():
            self.fail_dict[k] = v

    def exit_json(self, **kwargs):
        for k, v in kwargs.items():
            self.exit_dict[k] = v


def mock_bases(test, klass):
    original_bases = klass.__bases__
    klass.__bases__ = (AnsibleModuleMock,)
    test.addCleanup(restore_bases, klass, original_bases)


def restore_bases(klass, bases):
    klass.__bases__ = bases
