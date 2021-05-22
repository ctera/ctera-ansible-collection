#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, CTERA Networks Ltd.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: ctera_portal_init_master
short_description: CTERA-Networks Portal Master Initialization
description:
    - Initialize Portal Master
extends_documentation_fragment:
    - ctera.ctera.vportal

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  email:
    description: The e-mail address of the user
    type: str
    required: True
  first_name:
    description: The first name of the user
    type: str
    required: True
  last_name:
    description: The first name of the user
    type: str
    required: True
  domain:
    description: The domain suffix for CTERA Portal
    type: str
    required: True

'''

EXAMPLES = '''
- name: initialize portal master
  ctera_portal_init_master:
    email: 'admin@example.com'
    first_name: 'Admin'
    last_name: 'Adminson'
    domain: 'ctera.me'
    ctera_host: "{{ ctera_portal_hostname }}"
    ctera_user: "{{ ctera_portal_user }}"
    ctera_password: "{{ ctera_portal_password }}"
'''

RETURN = r''' # '''

try:
    from cterasdk import portal_enum
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common

from ansible_collections.ctera.ctera.plugins.module_utils.ctera_portal_base import CteraPortalBase


class CteraPortalInitMaster(CteraPortalBase):
    _configure_params = ['email', 'first_name', 'last_name', 'domain']

    def __init__(self):
        super().__init__(
            dict(
                email=dict(type='str', required=True),
                first_name=dict(type='str', required=True),
                last_name=dict(type='str', required=True),
                domain=dict(type='str', required=True),
            ),
            login=False
        )

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Portal Initialization failed'

    def _execute(self):
        if self._is_already_configured():
            self.ansible_module.ctera_return_value().skipped().msg('The Portal Master Server is already configured ')
        else:
            self._configure_master()

    def _is_already_configured(self):
        setup_status = self._ctera_portal.setup.get_setup_status()
        return setup_status.wizard == portal_enum.SetupWizardStage.Finish

    def _configure_master(self):
        configure_params = {k: v for k, v in self.parameters.items() if k in CteraPortalInitMaster._configure_params}
        configure_params['name'] = self.parameters['ctera_user']
        configure_params['password'] = self.parameters['ctera_password']
        self._ctera_portal.setup.init_master(**configure_params)


def main():  # pragma: no cover
    CteraPortalInitMaster().run()


if __name__ == '__main__':  # pragma: no cover
    main()
