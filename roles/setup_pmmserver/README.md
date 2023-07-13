# setup_pmmserver

This role is for configuring pmm client for PostgreSQL server.

## Requirements

Following are the requirements of this role.

1. Ansible

## Role Variables

When executing the role via ansible these are the required variables:

- **_pg_version_**

  Postgres Versions supported are: `14.0`, `14.1`, `14.2`, `14.3`,`14.3`, `14.5`, `14.6`

- **_pg_type_**

  Database Engine supported are: `PG`

These and other variables can be assigned in the `pre_tasks` definition of the
section: _How to include the `setup_pmmserver` role in your Playbook_

The rest of the variables can be configured and are available in the:

  * [roles/setup_pmmserver/defaults/main.yml](./defaults/main.yml)

Below is the documentation of the rest of the main variables:

### `pmm_server_port`

pmmserver port. Default: `443`.

Example:

```yaml
pmm_server_port: 443
```

## Dependencies

## Example Playbook

### Inventory file content

Content of the `inventory.yml` file:

```yaml
---
all:
  children:
    pmmserver:
      hosts:
        pmmserver1:
          ansible_host: xxx.xxx.xxx.xxx
          private_ip: xxx.xxx.xxx.xxx
```

### How to include the `setup_pmmserver` role in your Playbook

Below is an example of how to include the `setup_pmmserver` role:

```yaml
---
- hosts: all
  name: Deploy Pmm Client instances
  become: true
  gather_facts: true

  collections:
    - tmax_opensql.postgres

  pre_tasks:
    - name: Initialize the user defined variables
      set_fact:
        pg_version: 14.6
        pg_type: "PG"
        pmm_server_port: 443

  roles:
    - setup_pmmserver
```

Defining and adding variables is done in the `set_fact` of the `pre_tasks`.

All the variables are available at:

  * [roles/setup_pmmserver/defaults/main.yml](./defaults/main.yml)

## Database engines supported
### Supported OS
- CentOS7
- CentOS8

### Supported PostgreSQL Version
- 14.0 - 14.6

## License

BSD

## Author information

Author:
  * [Sang Myeung Lee](https://github.com/sungmu1)
