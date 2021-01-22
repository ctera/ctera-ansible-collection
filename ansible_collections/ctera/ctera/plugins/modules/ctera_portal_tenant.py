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
module: ctera_portal_tenant
short_description: CTERA-Networks Portal Tenant Management
description:
    - Manage Portal Tenants
extends_documentation_fragment:
    - ctera.ctera.vportal

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  state:
    description:
    - Whether the specified tenant should exist or not.
    type: str
    choices: ['present', 'absent']
    default: 'present'
  name:
    description: The name of the managed tenant
    type: str
    required: True
  display_name:
    description: The Display Name of the managed tenant
    type: str
  billing_id:
    description: The Billing ID for the managed tenant
    type: str
  company:
    description: The Company name for the managed tenant
    type: str
  plan:
    description: The Subscription plan name to assign to the managed tenant
    type: str
  comment:
    description: Assign a comment to the managed tenant
    type: str

'''

EXAMPLES = '''
- name: New Company tenant
  ctera_portal_tenant:
    name: Example
    display_name: "Tenant for the Example Company Ltd"
    company: "Example Company Ltd"
    ctera_host: "{{ ctera_portal_hostname }}"
    ctera_user: "{{ ctera_portal_user }}"
    ctera_password: "{{ ctera_portal_password }}"
'''

RETURN = r''' # '''

try:
    from cterasdk import CTERAException
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common

import ansible_collections.ctera.ctera.plugins.module_utils.ctera_common as ctera_common
from ansible_collections.ctera.ctera.plugins.module_utils.ctera_portal_base import CteraPortalBase


class CteraPortalTenant(CteraPortalBase):
    _create_params = ['name', 'display_name', 'billing_id', 'company', 'plan', 'comment']

    def __init__(self):
        super().__init__(
            dict(
                state=dict(choices=['present', 'absent'], default='present'),
                name=dict(required=True),
                display_name=dict(),
                billing_id=dict(),
                company=dict(),
                plan=dict(),
                comment=dict(),
            )
        )

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Tenant Management failed'

    def _execute(self):
        state = self.parameters.pop('state')
        tenant = self._get_tenant()
        if state == 'present':
            self._ensure_present(tenant)
        else:
            self._ensure_absent(tenant)

    def _ensure_present(self, tenant):
        if tenant:
            self._handle_modify(tenant)
        else:
            self._handle_create()

    def _handle_create(self):
        create_params = {k: v for k, v in self.parameters.items() if k in CteraPortalTenant._create_params}
        self._ctera_portal.portals.add(**create_params)
        self.ansible_module.ctera_return_value().changed().msg('Tenant was created').put(**create_params)

    def _handle_modify(self, tenant):
        messages = []
        changed = False

        if tenant.pop('activation_status') == 'Disabled':
            self._ctera_portal.portals.undelete(self.parameters['name'])
            changed = True
            messages.append('Tenant was undeleted')

        modified_attributes = ctera_common.get_modified_attributes(tenant, self.parameters)
        if modified_attributes:
            new_plan = modified_attributes.pop('plan', None)
            if new_plan is not None:
                self._ctera_portal.portals.subscribe(self.parameters['name'], new_plan)
                changed = True
                messages.append('Plan was changed')
                self.ansible_module.ctera_return_value().put(plan=new_plan)
            if modified_attributes:
                messages.append('Modifying tenant details is not supported')
        else:
            messages.append('Tenant details did not change')

        if changed:
            self.ansible_module.ctera_return_value().changed()
        else:
            self.ansible_module.ctera_return_value().skipped()
        self.ansible_module.ctera_return_value().put(name=self.parameters['name']).msg(' '.join(messages))

    def _ensure_absent(self, tenant):
        if tenant:
            self._ctera_portal.portals.delete(self.parameters['name'])
            self.ansible_module.ctera_return_value().changed().msg('Tenant deleted').put(name=self.parameters['name'])
        else:
            self.ansible_module.ctera_return_value().skipped().msg('Tenant already does not exist').put(name=self.parameters['name'])

    def _get_tenant(self):
        tenant = None
        try:
            tenant = self._ctera_portal.portals.get(
                self.parameters['name'],
                include=['name', 'displayName', 'externalPortalId', 'companyName', 'comment', 'plan', 'activationStatus']
            )
        except CTERAException:
            pass
        return self._to_tenant_dict(tenant) if tenant else None

    def _to_tenant_dict(self, tenant_obj):
        return {
            'name': tenant_obj.name,
            'display_name': tenant_obj.displayName,
            'billing_id': tenant_obj.externalPortalId,
            'company': tenant_obj.companyName,
            'comment': tenant_obj.comment,
            'plan': self._get_plan_name(tenant_obj.plan),
            'activation_status': tenant_obj.activationStatus
        }

    def _get_plan_name(self, plan_object_ref):
        plan = self._ctera_portal.get(plan_object_ref)
        return plan.name if plan is not None else None


def main():  # pragma: no cover
    CteraPortalTenant().run()


if __name__ == '__main__':  # pragma: no cover
    main()
