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
module: ctera_filer_ftp
short_description: Manage the FTP configuration of the CTERA-Networks filer
description:
    - Enable/Disable/Modify the FTP configuration of the CTERA-Networks filer
version_added: "2.10"
extends_documentation_fragment:
    - ctera.ctera.filer

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  enabled:
    description: Enable FTP
    type: bool
    default: True
  require_ssl:
    description: Allow only SSL/TLS connections
    type: bool
    default: False
  max_connections_per_ip:
    description: Maximum Connections per Client
    type: int
    default: 5
  banner_message:
    description: FTP Banner Message
    type: str
    default: Welcome to CTERA FTP.
  allow_anonymous_ftp:
    description: Allow anonymous FTP downloads
    type: bool
    default: False
  anonymous_ftp_folder:
    description: Anonymous FTP Directory
    type: str
  anonymous_download_limit:
    description: Limit download bandwidth of anonymous connection in KB/sec per connection. 0 for unlimited
    type: int
    default: 0
requirements:
    - cterasdk
'''

EXAMPLES = '''
- name: Configure FTP as default
  ctera_filer_ftp:
    filer_host: "{{ ctera_filer_hostname }}"
    filer_user: "{{ ctera_filer_user }}"
    filer_password: "{{ ctera_filer_password }}"
'''

RETURN = r''' # '''

from ansible_collections.ctera.ctera.plugins.module_utils.ctera_filer_share_config_base import CteraFilerShareConfigBase


class CteraFilerFtp(CteraFilerShareConfigBase):
    def __init__(self):
        super().__init__(
            dict(
                require_ssl=dict(type='bool', required=False, default=False),
                max_connections_per_ip=dict(type='int', required=False, default=5),
                banner_message=dict(type='str', required=False, default='Welcome to CTERA FTP.'),
                allow_anonymous_ftp=dict(type='bool', required=False, default=False),
                anonymous_ftp_folder=dict(type='str', required=False),
                anonymous_download_limit=dict(type='int', required=False, default=0),
            )
        )

    @property
    def _share_type(self):
        return "FTP"

    @property
    def _manager(self):
        return self._ctera_filer.ftp

    def _to_config_dict(self, config):
        return dict(
            mode=config.mode,
            allow_anonymous_ftp=config.AllowAnonymousFTP,
            anonymous_download_limit=config.AnonymousDownloadLimit,
            anonymous_ftp_folder=config.AnonymousFTPFolder,
            banner_message=config.BannerMessage,
            max_connections_per_ip=config.MaxConnectionsPerIP,
            require_ssl=config.RequireSSL
        )


def main():  # pragma: no cover
    CteraFilerFtp().run()


if __name__ == '__main__':  # pragma: no cover
    main()
