# setup_pmmclient

This role is for configuring pmm client for PostgreSQL server.

## Requirements

Following are the requirements of this role.

1. Ansible
2. `tmax_opensql.postgres` -> `setup_pmmserver` role for setting the repository on
   the systems.

## Role Variables

When executing the role via ansible these are the required variables:

- **_pg_version_**

  Postgres Versions supported are: `14.0`, `14.1`, `14.2`, `14.3`,`14.3`, `14.5`, `14.6`, `14.7`, `14.8`, `15.0`, `15.1`, `15.2`, `15.3`

- **_pg_type_**

  Database Engine supported are: `PG`

These and other variables can be assigned in the `pre_tasks` definition of the
section: _How to include the `setup_pmmclient` role in your Playbook_

The rest of the variables can be configured and are available in the:

  * [roles/setup_pmmclient/defaults/main.yml](./defaults/main.yml)
  * [roles/setup_pmmclient/vars/PG.yml](./vars/main.yml)
  * [roles/setup_pmmclient/vars/PG.yml](./vars/PG_RedHat.yml)
  * [roles/setup_pmmclient/vars/PG.yml](./vars/PG_Debian.yml)

Below is the documentation of the rest of the main variables:

### `pmm_server_port`

pmmserver port. Default: `443`.

Example:

```yaml
pmm_server_port: 443
```

## Dependencies

This role does not have any dependencies, but packages repositories should have
been configured beforehand with the `setup_repo` role.

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

    primary:
      hosts:
        primary1:
          ansible_host: xxx.xxx.xxx.xxx
          private_ip: xxx.xxx.xxx.xxx
          pmm_client: true
          pmm_server_host: xxx.xxx.xxx.xxx
    standby:
      hosts:
        standby1:
          ansible_host: xxx.xxx.xxx.xxx
          private_ip: xxx.xxx.xxx.xxx
          upstream_node_private_ip: xxx.xxx.xxx.xxx
          replication_type: synchronous
          pmm_client: true
          pmm_server_host: xxx.xxx.xxx.xxx
        standby2:
          ansible_host: xxx.xxx.xxx.xxx
          private_ip: xxx.xxx.xxx.xxx
          upstream_node_private_ip: xxx.xxx.xxx.xxx
          replication_type: asynchronous
          pmm_client: true
          pmm_server_host: xxx.xxx.xxx.xxx
```

### How to include the `setup_pmmclient` role in your Playbook

Below is an example of how to include the `setup_pmmclient` role:

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
    - setup_repo
    - install_dbserver
    - init_dbserver
    - setup_pmmserver
    - setup_pmmclient
```

Defining and adding variables is done in the `set_fact` of the `pre_tasks`.

All the variables are available at:

  * [roles/setup_pmmclient/defaults/main.yml](./defaults/main.yml)

## Database engines supported
### Supported OS
- CentOS7
- CentOS8
- Rocky8
- Rocky9

### Supported PostgreSQL Version
- 14.0 - 14.8
- 15.0 - 15.3

## License

BSD

## Author information

Author:
  * [Sang Myeung Lee](https://github.com/sungmu1)
