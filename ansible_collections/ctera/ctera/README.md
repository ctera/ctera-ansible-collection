# Ansible Collection for CTERA
[![Build Status](https://travis-ci.com/ctera/ctera-ansible-collections.svg?branch=master)](https://travis-ci.com/ctera/ctera-ansible-collections)
[![Coverage Status](https://coveralls.io/repos/github/ctera/ctera-ansible-collections/badge.svg?branch=master)](https://coveralls.io/github/ctera/ctera-ansible-collections?branch=master)

This collection provides a series of Ansible modules and plugins for interacting with the [CTERA](https://www.ctera.com) Filer and Portal.

## Requirements

- ansible version >= 2.9
- [CTERA Python SDK](https://github.com/ctera/ctera-python-sdk)

## Installation
To install CTERA collection hosted in Galaxy:

```bash
ansible-galaxy collection install ctera.ctera
```

To upgrade to the latest version of CTERA collection:

```bash
ansible-galaxy collection install ctera.ctera --force
```

### Playbooks

To use a module from CTERA collection, please reference the full namespace, collection name, and modules name that you want to use:

```yaml
---
- name: Configure the CTERA Edge Filer
  hosts: localhost
  vars:
    filer_host: 192.168.179.128
    filer_user: admin
    filer_password: Gr8Password!
  tasks:
  - name: cloud services
    ctera.ctera.ctera_filer_cloud_services:
      state: 'connected'
      server: 192.168.68.122
      user: ygal
      password: Gr8erPassword!
      filer_host: "{{ filer_host }}"
      filer_user: "{{ filer_user }}"
      filer_password: "{{ filer_password }}"
```

Or you can add full namepsace and collection name in the `collections` element:

```yaml
---
- name: Configure the CTERA Edge Filer
  hosts: localhost
  collections:
    - ctera.ctera
  vars:
    filer_host: 192.168.179.128
    filer_user: admin
    filer_password: Gr8Password!
  tasks:
  - name: cloud services
    ctera_filer_cloud_services:
      state: 'connected'
      server: 192.168.68.122
      user: ygal
      password: Gr8erPassword!
      filer_host: "{{ filer_host }}"
      filer_user: "{{ filer_user }}"
      filer_password: "{{ filer_password }}"
```

## License

[Apache License 2.0](../../../LICENSE)
