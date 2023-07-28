# setup_extension

This Ansible Role install and manage PostgreSQL Extension

## Requirements

1. Ansible
2. `tmax_opensql.postgres` -> `setup_repo` - for Installing the PG repository

## Role variables

When executing the role via Ansible these are required variables:

- **pg_version**

    Postgres Version supported are: `14.0`, `14.1`, `14.2`, `14.3`,`14.3`, `14.5`, `14.6`, `14.7`, `14.8`, `15.0`, `15.1`, `15.2`, `15.3`

- **pg_type**

    Database Engine supported are: `PG`

### `pg_extension_list`

Extension supported are: `potgis`, `pgaudit`, `pg_hint_plan`, `plpython3u`, `pg_bigm`, `sslutils`

Default: `potgis`, `pgaudit`, `pg_hint_plan`, `plpython3u`, `pg_bigm`, `sslutils`

Example:

```yaml
pg_extension_list:
    - postgis
    - pgaudit
    - pg_hint_plan
    - plpython3u
    - pg_bigm
    - sslutils
```

The rest of the variables can be configured and are available in the:

- [roles/setup_extension/defaults/main.yml](./defaults/main.yml)
- [roles/setup_extension/vars/PG_RedHat7.yml](./vars/PG_RedHat7.yml)
- [roles/setup_extension/vars/PG_RedHat8.yml](./vars/PG_RedHat8.yml)
- [roles/setup_extension/vars/PG_RedHat9.yml](./vars/PG_RedHat9.yml)
- [roles/setup_extension/vars/PG_Debian.yml](./vars/PG_Debian.yml)



## Dependencies

setup_repo: packages repositories should have been configured beforehand with the setup_repo role.
install_dbserver: Postgres binaries are required for this role.
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
            - pg_hint_plan
            - plpython3u
            - pg_bigm
            - sslutils
  roles:
    - setup_extension
```

## Database engines supported

### Supported OS
- CentOS7
- CentOS8
- Rocky8
- Rocky9

### Supported PostgreSQL Version
- 14.0 - 14.8
- 15.0 - 15.3

## PostgreSQL extension supported

- RedHat
  * PostGIS : 3.2
  * pgAudit : 1.6
  * pg_bigm_version: 1.2
  * pg_hint_plan_version: 1.4.1
  * sslutils: 1.3

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
