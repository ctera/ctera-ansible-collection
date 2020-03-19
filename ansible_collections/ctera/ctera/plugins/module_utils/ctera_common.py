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

import traceback

try:
    from cterasdk import CTERAException
    CTERASDK_IMP_ERR = None
    HAS_CTERASDK = True
except ImportError:  # pragma: no cover
    CTERASDK_IMP_ERR = traceback.format_exc()
    HAS_CTERASDK = False


class Object:
    pass


class AnsibleReturnValue:  # pylint: disable=attribute-defined-outside-init
    def __init__(self):
        self.param = Object()
        self.param.failed = False

    def changed(self):
        self.param.changed = True
        return self

    def has_failed(self):
        return self.param.failed

    def failed(self):
        self.param.failed = True
        return self

    def skipped(self):
        self.param.skipped = True
        return self

    def msg(self, msg):
        self.param.msg = msg
        return self

    def rc(self, rc):
        self.param.rc = rc
        return self

    def warning(self, warning):
        if not hasattr(self.param, 'warnings'):
            self.param.warnings = [warning]
        else:
            self.param.warnings.append(warning)
        return self

    def put(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self.param, key, value)
        return self

    def as_dict(self):
        return self.param.__dict__


def object_exists(ctera_host, path):
    try:
        ctera_object = ctera_host.get(path)
        return (True, ctera_object)
    except CTERAException:
        return (False, None)


def get_parameters(ansible_params):
    parameters = dict()
    for param in ansible_params:
        if ansible_params[param] is not None:
            parameters[param] = ansible_params[param]
    return parameters


def filter_parameters(parameters, filter_list):
    return {k: v for k, v in parameters.items() if k in filter_list}


def cmp(a, b):
    """
    Python 3 does not have a cmp function, this will do the cmp.
    :param a: first object to check
    :param b: second object to check
    :return:
    """
    # convert to lower case for string comparison.
    if a is None:
        return -1
    # Checking both sides
    if not (isinstance(a, type(b)) and isinstance(b, type(a))):
        return -1
    if isinstance(a, str) and isinstance(b, str):
        a = a.lower()
        b = b.lower()
    # if list has string element, convert string to lower case.
    if isinstance(a, list) and isinstance(b, list):
        a = [x.lower() if isinstance(x, list) else x for x in a]
        b = [x.lower() if isinstance(x, list) else x for x in b]
        a.sort()
        b.sort()
    return (a > b) - (a < b)


def compare_lists(current, desired, get_list_diff):
    ''' compares two lists and return a list of elements that are either the desired elements or elements that are
        modified from the current state depending on the get_list_diff flag
        :param: current: current item attribute
        :param: desired: attributes from playbook
        :param: get_list_diff: specifies whether to have a diff of desired list w.r.t current list for an attribute
        :return: list of attributes to be modified
        :rtype: list
    '''
    desired_diff_list = [item for item in desired if item not in current]  # get what in desired and not in current
    current_diff_list = [item for item in current if item not in desired]  # get what in current but not in desired

    if desired_diff_list or current_diff_list:
        # there are changes
        if get_list_diff:
            return desired_diff_list
        return desired
    return []


def get_modified_attributes(current, desired, get_list_diff=False):
    ''' takes two dicts of attributes and return a dict of attributes that are
        not in the current state
        It is expected that all attributes of interest are listed in current and
        desired.
        :param: current: current attributes
        :param: desired: attributes from playbook
        :param: get_list_diff: specifies whether to have a diff of desired list w.r.t current list for an attribute
        :return: dict of attributes to be modified
        :rtype: dict
    '''
    # if the object does not exist,  we can't modify it
    modified = dict()
    if current is None:
        return modified

    # collect changed attributes
    for key, value in current.items():
        if key in desired and desired[key] is not None:
            if isinstance(value, list):
                modified_list = compare_lists(value, desired[key], get_list_diff)  # get modified list from current and desired
                if modified_list:
                    modified[key] = modified_list
            elif cmp(value, desired[key]) != 0:
                modified[key] = desired[key]
    return modified


def set_result(ansible_module, messages):
    changed_message = ''
    skipped_message = ''
    if len(messages['changed']) > 0:
        ansible_module.ctera_return_value().changed()
        changed_message = "Changed: " + " ".join(messages['changed'])
    if len(messages['skipped']) > 0:
        if len(messages['changed']) == 0:
            ansible_module.ctera_return_value().skipped()
        skipped_message = "Skipped: " + " ".join(messages['skipped'])

    if changed_message and skipped_message:
        message = ' '.join([changed_message, skipped_message])
    elif changed_message:
        message = changed_message
    elif skipped_message:
        message = skipped_message
    else:
        message = ''

    if message:
        ansible_module.ctera_return_value().msg(message)
