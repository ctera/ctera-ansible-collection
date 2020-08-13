# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    # Documentation fragment for CTERA Portal (ctera)
    DOCUMENTATION = r'''
extends_documentation_fragment:
    - ctera.ctera.ctera
options:
  tenant:
    description:
    - Name of the tenant.
    - For Global Admin operations set to "$admin"
    - Use default if not provided.
    - Do not set for initialization operations
    type: str

'''
