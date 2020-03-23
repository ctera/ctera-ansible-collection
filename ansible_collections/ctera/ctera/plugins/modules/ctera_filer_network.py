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
module: ctera_filer_network
short_description: CTERA-Networks filer network configuration
description:
    - Configure the network of a CTERA-Networks filer
version_added: "2.10"
extends_documentation_fragment:
    - ctera.ctera.filer

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  mode:
    description: IP addressing mode
    type: str
    choices:
      - dynamic
      - static
    default: dynamic
  address:
    description: IP Address. Required if I(mode=static)
    type: str
  subnet:
    description: IP Subnet. Required if I(mode=static)
    type: str
  gateway:
    description: Default gateway. Required if I(mode=static)
    type: str
  primary_dns_server:
    description: Primary DNS Server. Required if I(mode=static)
    type: str
  secondary_dns_server:
    description: Secondary DNS Server
    type: str

requirements:
    - cterasdk
'''

EXAMPLES = '''
- name: Use DHCP
  ctera_filer_network:
    filer_host: "{{ ctera_filer_hostname }}"
    filer_user: "{{ ctera_filer_user }}"
    filer_password: "{{ ctera_filer_password }}"

- name: Set DNS Server
  ctera_filer_network:
    primary_dns_server: 8.8.8.8
    filer_host: "{{ ctera_filer_hostname }}"
    filer_user: "{{ ctera_filer_user }}"
    filer_password: "{{ ctera_filer_password }}"

- name: Set IP Address
  ctera_filer_network:
    address: 192.168.1.10
    subnet: 255.255.255.0
    gateway: 192.168.1.1
    primary_dns_server: 8.8.8.8
    filer_host: "{{ ctera_filer_hostname }}"
    filer_user: "{{ ctera_filer_user }}"
    filer_password: "{{ ctera_filer_password }}"
'''

RETURN = r''' # '''


import ansible_collections.ctera.ctera.plugins.module_utils.ctera_common as ctera_common
from ansible_collections.ctera.ctera.plugins.module_utils.ctera_filer_base import CteraFilerBase

try:
    from cterasdk import gateway_enum
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common


class CteraFilerNetwork(CteraFilerBase):
    _set_static_params = ['address', 'subnet', 'gateway', 'primary_dns_server', 'secondary_dns_server']

    def __init__(self):
        super().__init__(
            dict(
                mode=dict(required=False, type='str', choices=['dynamic', 'static'], default='dynamic'),
                address=dict(type='str', required=False),
                subnet=dict(type='str', required=False),
                gateway=dict(type='str', required=False),
                primary_dns_server=dict(type='str', required=False),
                secondary_dns_server=dict(type='str', required=False)
            ),
            required_if=[
                ('mode', 'static', ['address', 'subnet', 'gateway', 'primary_dns_server'])
            ],
            required_by=dict(
                secondary_dns_server=['primary_dns_server']
            )
        )

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Network management failed'

    def _execute(self):
        mode = self.parameters.pop('mode')
        config = self._get_current_config()
        if mode == 'dynamic':
            self._ensure_dynamic(config)
        else:
            self._ensure_static(config)

    def _ensure_dynamic(self, config):
        messages = {
            'changed': [],
            'skipped': []
        }
        if config['mode'] == 'dynamic':
            messages['skipped'].append("IP addressing mode is already set to dynamic")
        else:
            self._ctera_filer.network.enable_dhcp()
            messages['changed'].append("IP addressing mode changed to dynamic")

        if self.parameters.get('primary_dns_server'):
            self._ensure_dns_servers(config, messages)
        ctera_common.set_result(self.ansible_module, messages)

    def _ensure_dns_servers(self, config, messages):
        primary_dns_server = self.parameters['primary_dns_server']
        secondary_dns_server = self.parameters.get('secondary_dns_server')
        if primary_dns_server != config['primary_dns_server'] or secondary_dns_server != config['secondary_dns_server']:
            self._ctera_filer.network.set_static_nameserver(primary_dns_server, secondary_dns_server=secondary_dns_server)
            messages['changed'].append("DNS Servers were set")
        else:
            messages['skipped'].append("DNS Servers did not change")

    def _ensure_static(self, config):
        modified_attributes = ctera_common.get_modified_attributes(config, self.parameters)
        if config['mode'] == 'static' and not modified_attributes:
            self.ansible_module.ctera_return_value().msg("IP Configuration did not change")
            return
        self._ctera_filer.network.set_static_ipaddr(**ctera_common.filter_parameters(self.parameters, CteraFilerNetwork._set_static_params))
        self.ansible_module.ctera_return_value().changed().msg("IP Configuration set")

    def _get_current_config(self):
        return self._to_config_dict(self._ctera_filer.network.ifconfig().ip)

    def _to_config_dict(self, config):
        return dict(
            mode='dynamic' if config.DHCPMode == gateway_enum.Mode.Enabled else 'static',
            address=config.address,
            subnet=config.netmask,
            gateway=config.gateway,
            primary_dns_server=config.DNSServer1,
            secondary_dns_server=config.DNSServer2
        )


def main():  # pragma: no cover
    CteraFilerNetwork().run()


if __name__ == '__main__':  # pragma: no cover
    main()
