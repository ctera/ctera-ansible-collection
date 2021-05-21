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
module: ctera_portal_init_application_server
short_description: CTERA-Networks Portal Application Server Initialization
description:
    - Initialize Portal Application Server
extends_documentation_fragment:
    - ctera.ctera.vportal

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  ipaddr:
    description: The CTERA Portal application server IP address
    required: True
    type: str
  secret:
    description: A password or a PEM-encoded private key
    type: str

'''

EXAMPLES = '''
- name: initialize portal application server
  ctera_portal_init_application_server:
    ipaddr: 192.168.1.1
    secret: 'su@p3rsecret!!'
    ctera_host: "{{ ctera_app_hostname }}"
    ctera_user: "{{ ctera_app_user }}"
    ctera_password: "{{ ctera_app_password }}"
'''

RETURN = r''' # '''

try:
    from cterasdk import portal_enum
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common

from ansible_collections.ctera.ctera.plugins.module_utils.ctera_portal_base import CteraPortalBase


class CteraPortalInitApplication(CteraPortalBase):
    _configure_params = ['ipaddr', 'secret']

    def __init__(self):
        super().__init__(
            dict(
                ipaddr=dict(type='str', required=True),
                secret=dict(type='str', required=False, no_log=True),
            ),
            login=False
        )

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Portal Initialization failed'

    def _execute(self):
        if self._is_already_configured():
            self.ansible_module.ctera_return_value().skipped().msg('The Portal Application Server is already configured ')
            return
        self._configure_application_server()

    def _is_already_configured(self):
        setup_status = self._ctera_portal.setup.get_setup_status()
        return setup_status.wizard == portal_enum.SetupWizardStage.Finish

    def _configure_application_server(self):
        configure_params = {k: v for k, v in self.parameters.items() if k in CteraPortalInitApplication._configure_params}
        self._ctera_portal.setup.init_application_server(**configure_params)


def main():  # pragma: no cover
    CteraPortalInitApplication().run()


if __name__ == '__main__':  # pragma: no cover
    main()
