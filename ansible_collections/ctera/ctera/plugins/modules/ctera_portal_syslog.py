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
module: ctera_portal_syslog
short_description: CTERA Portal server management
description:
    - Forward log messages from CTERA Portal to a syslog server
extends_documentation_fragment:
    - ctera.ctera.vportal

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  state:
    description:
    - Whether forwarding log messages over syslog should be enabled or not.
    type: str
    choices: ['enabled', 'disabled']
    default: 'enabled'
  server:
    description: The syslog server ip addr, hostname or FQDN
    required: False
    type: str
  port:
    description: The new server name
    required: False
    type: int
  min_severity:
    description: Minimum severity of log messages to forward
    type: str
    choices:
    - emergency
    - alert
    - critical
    - error
    - warning
    - notice
    - info
    - debug
    required: False

'''

EXAMPLES = '''
- name: Configure a syslog server
  ctera.ctera.ctera_portal_syslog:
    server: "your.syslog.server.com"
    port: 514
    ctera_host: "{{ ctera_portal_hostname }}"
    ctera_user: "{{ ctera_portal_user }}"
    ctera_password: "{{ ctera_portal_password }}"
    ctera_trust_certificate: True
    tenant: "$admin"

'''

RETURN = r''' # '''

import ansible_collections.ctera.ctera.plugins.module_utils.ctera_common as ctera_common
from ansible_collections.ctera.ctera.plugins.module_utils.ctera_portal_base import CteraPortalBase


try:
    from cterasdk import CTERAException
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common


class CteraPortalSyslog(CteraPortalBase):

    def __init__(self):
        severity = ['info', 'error', 'warning', 'critical', 'alert', 'emergency', 'debug', 'notice']
        super().__init__(
            dict(
                state=dict(required=False, choices=['enabled', 'disabled'], default='enabled'),
                server=dict(type='str', required=False),
                port=dict(type='int', required=False),
                min_severity=dict(type='str', required=False, choices=severity)
            ),
            required_if=[('state', 'enabled', ['server'])]
        )

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Syslog management failed'

    def _execute(self):
        state = self.parameters.pop('state')
        if state == 'enabled':
            self._ensure_enabled()
        else:
            self._ensure_disabled()

    def _ensure_enabled(self):
        if self._ctera_portal.syslog.is_enabled():
            syslog_config = self._get_current_syslog_config()
            modified_attributes = ctera_common.get_modified_attributes(syslog_config, self.parameters)
            if modified_attributes:
                self._ctera_portal.syslog.modify(**modified_attributes)
                self.ansible_module.ctera_return_value().changed().msg('Syslog server configuration was modified')
            else:
                self.ansible_module.ctera_return_value().skipped().msg('Syslog server config did not change')
        else:
            self._ctera_portal.syslog.enable(self.parameters['server'])
            self.ansible_module.ctera_return_value().changed().msg('Syslog server enabled').put(server=self.parameters['server'])

    def _ensure_disabled(self):
        if self._ctera_portal.syslog.is_enabled():
            self._ctera_portal.syslog.disable()
            self.ansible_module.ctera_return_value().changed().msg('Syslog server disabled')
        else:
            self.ansible_module.ctera_return_value().skipped().msg('Syslog server is already disabled')

    def _get_current_syslog_config(self):
        syslog_config = self._ctera_portal.syslog.get_configuration()
        return dict(
            server=syslog_config.server,
            port=syslog_config.port,
            min_severity=syslog_config.minSeverity
        )


def main():  # pragma: no cover
    CteraPortalSyslog().run()


if __name__ == '__main__':  # pragma: no cover
    main()
