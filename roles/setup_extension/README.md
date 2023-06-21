# setup_extension

This Ansible Role install and manage PostgreSQL Extension

## Requirements

1. Ansible
2. `tmax_opensql.postgres` -> `setup_repo` - for Installing the PG repository

## Role variables

When executing the role via Ansible these are required variables:

- **pg_version**

    Postgres Version supported are: `14.0`, `14.1`, `14.2`, `14.3`, `14.3`, `14.5`, `14.6`

- **pg_type**

    Database Engine supported are: `PG`

### `pg_extension_list`

Extension supported are: `potgis`, `pgaudit`, `pg_hint_plan`, `plpython3u`, `pg_bigm`

Default: `potgis`, `pgaudit`, `pg_hint_plan`, `plpython3u`, `pg_bigm`

Example:

```yaml
# install only postgis
pg_extension_list:
    - postgis
    - pgaudit
```
### `pg_extension_creates`

Add extensions to postgresql's shared_preload_libraries, and add the extension to the working PostgreSQL server.
This parameter can be used when PostgreSQL directories are structured and PostgreSQL is running.

Default: false

Example:

```yaml
extensioni_creates: true
```

The rest of the variables can be configured and are available in the:

- [roles/setup_extension/defaults/main.yml](./defaults/main.yml)
- [roles/setup_extension/vars/PG_RedHat.yml](./vars/PG_RedHat.yml)
- [roles/setup_extension/vars/PG_Debian.yml](./vars/PG_Debian.yml)


## Dependencies

This role depends on the `common`, `manage_dbserver`, `install_dbserver` role.

## Example Playbook

### Example of inventory file

Content of the `inventory.yml` file:

```yaml
all:
  children:
    primary:
      hosts:
        primary1:
          ansible_host: 192.168.122.1
          private_ip: 10.0.0.1
    standby:
      hosts:
        standby1:
          ansible_host: 192.168.122.2
          private_ip: 10.0.0.2
          upstream_node_private_ip: 10.0.0.1
          replication_type: synchronous
        standby2:
          ansible_host: 192.168.122.3
          private_ip: 10.0.0.3
          upstream_node_private_ip: 10.0.0.1
          replication_type: asynchronous
```


### How to include the `setup_extension` role in your Playbook

Below is an example of how to include the `setup_extension` role for
installing extension :

```yaml
---
- hosts: all
  name: Install Extension
  become: yes
  gather_facts: yes

  collections:
    - tmax_opensql.postgres

  pre_tasks:
    - name: Initialize the user defined variables
      set_fact:
        pg_version: 14.6
        pg_type: "PG"

        pg_extension_list:
            - postgis
            - pgaudit

  roles:
    - setup_extension
```

## Database engines supported

### Supported OS
- CentOS7
- CentOS8

### Supported PostgreSQL Version
- 14.0 - 14.6

## PostgreSQL extension supported

- RedHat
  * PostGIS : 3.2
  * pgAudit : 1.6

## Playbook execution examples
```bash
# To deploy community Postgres version 14.6 on CentOS8 hosts with the user centos
$ ansible-playbook playbook.yml \
  -u centos \
  -i inventory.yml \
  --extra-vars="pg_version=14.6 pg_type=PG"
```

## License

BSD

## Author information
Author:
  * [Sang Myeung Lee](https://github.com/sungmu1)
