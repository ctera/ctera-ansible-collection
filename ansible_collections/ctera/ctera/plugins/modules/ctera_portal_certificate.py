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
module: ctera_portal_certificate
short_description: CTERA Portal SSL certificate management
description:
    - Import and update the Portal's SSL certificate.
extends_documentation_fragment:
    - ctera.ctera.vportal

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  private_key:
    description: The private key
    required: True
    type: str
  server_certificate:
    description: The server SSL certificate
    required: True
    type: str
  certificate_chain:
    description: The SSL certificate chain
    required: True
    type: list
    elements: str
  force_update:
    description: Force the import of the SSL certificate chain
    type: bool
    default: False

'''

EXAMPLES = '''
- name: Import an SSL certificate to CTERA Portal
  ctera.ctera.ctera_portal_certificate:
    private_key: "{{ lookup('file', 'private.key') }}"
    server_certificate: "{{ lookup('file', 'certificate.crt') }}"
    certificate_chain:
      - "{{ lookup('file', 'certificate1.crt') }}"
      - "{{ lookup('file', 'certificate2.crt') }}"
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
    from cterasdk.lib import X509Certificate
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common


class CteraPortalCertificate(CteraPortalBase):
    _create_params = ['private_key', 'server_certificate', 'certificate_chain', 'force_update']

    def __init__(self):
        super().__init__(
            dict(
                private_key=dict(type='str', required=True, no_log=True),
                server_certificate=dict(type='str', required=True),
                certificate_chain=dict(type='list', elements='str', required=True),
                force_update=dict(type='bool', default=False)
            )
        )

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'SSL certificate management failed'

    def _execute(self):
        current_cert_thumbprint = self._get_thumbprint()
        new_cert_thumbprint = X509Certificate.load_certificate(self.parameters['server_certificate']).sha1_fingerprint
        if self.parameters.pop('force_update') or current_cert_thumbprint != new_cert_thumbprint:
            self._import_certificate()
            self.ansible_module.ctera_return_value().changed().msg('SSL certificate was updated')
        else:
            self.ansible_module.ctera_return_value().skipped().msg('No update required. SSL certificate did not change').put(thumbprint=current_cert_thumbprint)

    def _get_thumbprint(self):
        return self._ctera_portal.ssl.thumbprint

    def _import_certificate(self):
        private_key = self.parameters.pop('private_key')
        server_certificate = self.parameters.pop('server_certificate')
        certificate_chain = self.parameters.pop('certificate_chain')
        certificate_chain.insert(0, server_certificate)
        self._ctera_portal.ssl.import_from_chain(private_key, *certificate_chain)


def main():  # pragma: no cover
    CteraPortalCertificate().run()


if __name__ == '__main__':  # pragma: no cover
    main()
