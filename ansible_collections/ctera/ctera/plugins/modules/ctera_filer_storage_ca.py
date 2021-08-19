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
module: ctera_filer_storage_ca
short_description: CTERA Edge Filer Storage CA Certificate Management
description:
    - Import and update the Edge Filer's Storage CA certificate.
extends_documentation_fragment:
    - ctera.ctera.ctera

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  certificate:
    description: The CA certificate
    required: True
    type: str
  force_update:
    description: Force the import of the CA certificate
    type: bool
    default: False

'''

EXAMPLES = '''
- name: Import a a Storage CA Certificate to the Edge Filer
  ctera.ctera.ctera_filer_storage_ca:
    certificate: "{{ lookup('file', 'storage.crt') }}"
    ctera_host: "{{ ctera_filer_hostname }}"
    ctera_user: "{{ ctera_filer_user }}"
    ctera_password: "{{ ctera_filer_password }}"
    ctera_trust_certificate: True

'''

RETURN = r''' # '''

from ansible_collections.ctera.ctera.plugins.module_utils.ctera_filer_base import CteraFilerBase

try:
    from cterasdk.lib import X509Certificate
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common


class CteraFilerStorageCA(CteraFilerBase):
    _create_params = ['certificate', 'force_update']

    def __init__(self):
        super().__init__(
            dict(
                certificate=dict(type='str', required=True),
                force_update=dict(type='bool', default=False)
            )
        )

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Storage CA certificate Management Failed'

    def _execute(self):
        current_storage_ca = self._get_storage_ca()
        new_storage_ca = X509Certificate.load_certificate(self.parameters['certificate'])
        if not current_storage_ca or self.parameters['force_update'] or \
           new_storage_ca.subject not in current_storage_ca.subjectName or \
           new_storage_ca.issuer not in current_storage_ca.issuerName:
            self._import_certificate()
            self.ansible_module.ctera_return_value().changed().msg('Storage CA certificate was updated')
        else:
            self.ansible_module.ctera_return_value().skipped().msg('No update required. Storage CA certificate did not change')

    def _get_storage_ca(self):
        current_storage_ca = self._ctera_filer.ssl.get_storage_ca()
        return None if (current_storage_ca.subjectName is None or current_storage_ca.issuerName is None) else current_storage_ca

    def _import_certificate(self):
        certificate = self.parameters['certificate']
        self._ctera_filer.ssl.import_storage_ca(certificate)


def main():  # pragma: no cover
    CteraFilerStorageCA().run()


if __name__ == '__main__':  # pragma: no cover
    main()
