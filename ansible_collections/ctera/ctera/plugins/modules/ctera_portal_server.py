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
module: ctera_portal_server
short_description: CTERA Portal server management
description:
    - Modify the configuration of a CTERA Portal server
extends_documentation_fragment:
    - ctera.ctera.vportal

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  name:
    description: The current server name
    required: True
    type: str
  server_name:
    description: The new server name
    required: False
    type: str
  app:
    description: Enable or disable the application service
    required: False
    type: bool
  preview:
    description: Enable or disable the preview service
    required: False
    type: bool
  enable_public_ip:
    description: Enable or disable public NAT address
    required: False
    type: bool
  public_ip:
    description: Public NAT address
    required: False
    type: str
  allow_user_login:
    description: Allow or disallow logins to this server
    required: False
    type: bool
  enable_replication:
    description: Enable or disable database replication
    required: False
    type: bool
  replica_of:
    description: Configure as a replicate of another Portal server
    required: False
    type: str


'''

EXAMPLES = '''
- name: Rename a CTERA Portal server
  ctera.ctera.ctera_portal_server:
    name: "server"
    server_name: "main_database"
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


class CteraPortalServer(CteraPortalBase):

    def __init__(self):
        super().__init__(
            dict(
                name=dict(type='str', required=True),
                server_name=dict(type='str', required=False),
                app=dict(type='bool', required=False),
                preview=dict(type='bool', required=False),
                enable_public_ip=dict(type='bool', required=False),
                public_ip=dict(type='str', required=False),
                allow_user_login=dict(type='bool', required=False),
                enable_replication=dict(type='bool', required=False),
                replica_of=dict(type='str', required=False)
            ),
            required_if=[('enable_replication', True, ['replica_of']), ('enable_public_ip', True, ['public_ip'])]
        )

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Server management failed'

    def _execute(self):
        server = self._get_server()
        if server:
            modified_attributes = ctera_common.get_modified_attributes(server, self.parameters)
            if modified_attributes:
                self._ctera_portal.servers.modify(self.parameters['name'], **modified_attributes)
                self.ansible_module.ctera_return_value().changed().msg('Server modified').put(name=self.parameters['name'])
            else:
                self.ansible_module.ctera_return_value().skipped().msg('Server configuration did not change').put(name=self.parameters['name'])

    def _get_server(self):
        server = None
        try:
            server = self._ctera_portal.servers.get(name=self.parameters['name'])
        except CTERAException as error:
            if error.response.code != 404:  # pylint: disable=no-member
                raise
        return self._to_server_dict(server) if server else None

    @staticmethod
    def _to_server_dict(server):
        return dict(
            server_name=server.name,
            app=server.isApplicationServer,
            preview=server.renderingServer,
            enable_public_ip=True if server.publicIpaddr else False,
            public_ip=server.publicIpaddr,
            allow_user_login=server.allowUserLogin,
            enable_replication=True if server.replicationSettings is not None else False,
            replica_of=getattr(server.replicationSettings, 'replicationOf', None)
        )


def main():  # pragma: no cover
    CteraPortalServer().run()


if __name__ == '__main__':  # pragma: no cover
    main()
