import unittest.mock as mock

def mock_gateway_ansible_module(test, path):
    class_mock = test.patch_call(path)
    obj_mock = class_mock.return_value
    obj_mock.params = {}
    obj_mock.ctera_filer = mock.MagicMock()
    obj_mock.ctera_logout = mock.MagicMock()
    obj_mock.ctera_exit = mock.MagicMock()
    obj_mock.ctera_return_value = mock.MagicMock()
    return obj_mock
