# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    # Documentation fragment for FILER (ctera_filer)
    DOCUMENTATION = r'''
options:
  filer_host:
    description: IP Address or FQDN of the CTERA Networks Filer
    required: True
    type: str
  filer_user:
    description: User Name for communicating with the CTERA Networks Filer
    required: True
    type: str
  filer_password:
    description: Password of the user
    required: True
    type: str
  filer_trust_certificate:
    description: Trust unverified certificates
    type: bool
    default: False

requirements:
  - A physical or virtual CTERA-Networks Gateway
  - Ansible 2.8
  - Python3 cterasdk. Install using 'pip install cterasdk'

'''
