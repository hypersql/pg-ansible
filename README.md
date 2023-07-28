# PG Ansible

[![Version on Galaxy](https://img.shields.io/badge/dynamic/json?style=flat&label=ansible-galalxy&prefix=v&url=https://galaxy.ansible.com/api/v2/collections/tmax_opensql/postgres/&query=latest_version.version)](https://galaxy.ansible.com/tmax_opensql/postgres)

This repository is for hosting an Ansible Galaxy Collection **tmax_opensql.postgres** which helps users easily deploy Tmax OpenSQL package for PostgreSQL.

_The ansible playbook must be executed under an account that has full
privileges._

The following table describes the roles included in **tmax_opensql.postgres** collection.

| Role name                                                        | Description                                                                                                                                                                                            |
| ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [autotuning](roles/autotuning/README.md)                         | The autotuning role configures the system and Postgres instances for optimal performances. Most of the configuration values are calculated automatically from available resources found on the system. |
| [init_dbserver](roles/init_dbserver/README.md)                   | Initialize the PostgreSQL cluster (data) directory.                                                                                                                                                    |
| [install_dbserver](roles/install_dbserver/README.md)             | Install PostgreSQL database server packages.                                                                                                                                                           |
| [setup_extension](roles/setup_extension/README.md)               | Install PostgreSQL Extension packages.                                                                                                                                                    |
| [manage_dbserver](roles/manage_dbserver/README.md)               | Manage PostgreSQL clusters and covers common tasks.                                                                                                                                                    |
| [manage_pgbouncer](roles/manage_pgbouncer/README.md)             | Manage PgBouncer pools list and users.                                                                                                                                                                 |
| [manage_pgpool2](roles/manage_pgpool2/README.md)                 | Manage Pgpool-II settings and users.                                                                                                                                                                   |
| [manage_barmanbackup](roles/manage_barmanbackup/README.md)       | Set up PostgreSQL backups with Barman.                                                                                                                                                                 |
| [setup_barmanserver](roles/setup_barmanserver/README.md)         | Set up Barman (Postgres backup) server.                                                                                                                                                                |                                                                                                                       |
| [setup_pgbouncer](roles/setup_pgbouncer/README.md)               | Set up PgBouncer connection pooler.                                                                                                                                                                    |
| [setup_pgpool2](roles/setup_pgpool2/README.md)                   | Set up Pgpool-II connection pooler/load balancer.                                                                                                                                                      |
| [setup_pmmclient](roles/setup_pmmclient/README.md)                   | Set up PMM client.                                                                                                                                                        |
| [setup_pmmserver](roles/setup_pmmserver/README.md)                   | Set up PMM server.                                                                                                                                                      |
| [setup_replication](roles/setup_replication/README.md)           | Set up the data replication (synchronous/asynchronous).                                                                                                                                                |
| [setup_repmgr](roles/setup_repmgr/README.md)                     | Set up Repmgr for PostgreSQL HA cluster.                                                                                                                                                               |
| [setup_repo](roles/setup_repo/README.md)                         | Set up the PostgreSQL Community and EPEL repositories.                                                                                                                                                 |

## Pre-Requisites

For correctly installed and configuration of the cluster following are requirements:

1. Ansible (on the machine on which playbook will be executed).
2. Operating system privileged user (user with sudo privilege) on all the
   servers/virtual machines.
3. Machines for the Postgres cluster should have at least 2 CPUs and
   4 GB of RAM
4. The machine utilized for deploying with ansible can be a minimal instance

## Installation

To install Ansible: **[Installing Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)**

**tmax_opensql.postgres** can be installed in the following approaches:

### Installing from Ansible Galaxy

Use the command below to install **tmax_opensql.postgres**:

```bash
ansible-galaxy collection install tmax_opensql.postgres --force
```

This approach automatically makes the **tmax_opensql.postgres** collection available to
your playbooks.

A message indicating where the collection is installed will be displayed by
ansible-galaxy. The collection code should be automatically made readily
available for you.

By default the location of your installed collection is:
`~/.ansible/collections/ansible_collections`

### Cloning the source code from the repository GitHub

Use the command below to install **tmax_opensql.postgres**:

```bash
git clone https://github.com/tmaxopensql/pg-ansible.git
cd pg-ansible
make install
```

This approach automatically makes the **tmax_opensql.postgres** collection available to
your playbooks.

A message indicating where the collection is installed will be displayed by
ansible-galaxy. The collection code should be automatically made readily
available for you.

By default the location of your installed collection is:
`~/.ansible/collections/ansible_collections`

## Example of inventory file

Content of the `inventory.yml` file:

```yaml
---
all:
  children:
    primary:
      hosts:
        primary1:
          ansible_host: 110.0.0.1
          private_ip: 10.0.0.1
    standby:
      hosts:
        standby1:
          ansible_host: 110.0.0.2
          private_ip: 10.0.0.2
          upstream_node_private_ip: 10.0.0.1
          replication_type: synchronous
        standby2:
          ansible_host: 110.0.0.3
          private_ip: 10.0.0.3
          upstream_node_private_ip: 10.0.0.1
          replication_type: asynchronous
```

Note: don't forget to replace IP addresses.

## How to include the roles in your Playbook

Below is an example of how to include all the roles for a deployment in a
playbook:

```yaml
---
- hosts: all
  name: Postgres deployment playbook
  become: yes
  gather_facts: yes

  collections:
    - tmax_opensql.postgres

  pre_tasks:
    - name: Initialize the user defined variables
      set_fact:
        pg_version: 14.6
        pg_type: "PG"
        disable_logging: false

  roles:
    - role: setup_repo
    - role: install_dbserver
    - role: init_dbserver
    - role: setup_extension
    - role: setup_replication
    - role: setup_pgpool2
    - role: manage_pgpool2
    - role: manage_dbserver
    - role: setup_pgbackrest
    - role: setup_pgbackrestserver
    - role: setup_pgbouncer
    - role: manage_pgbouncer
    - role: setup_barmanserver
    - role: manage_barmanbackup
    - role: autotuning
```

You can customize the above example to install Tmax OpenSQL Package by selecting which roles you would like to execute.

## Default user and passwords

The following will occur should a password not be provided for the following
accounts:

- `pg_superuser`
- `pg_replication_user`

**Note:**

- The `~/.pgpassfile` folder and contained files are secured by assigning the
  permissions to `user` executing the playbook.
- The naming convention for the password file is: `<username>_pass`

## Playbook examples

Examples of utilizing the playbooks for installing Tmax OpenSQL Package are provided and located within the `playbook-examples` directory.

## SSH port configuration

When using non standard SSH port (different from 22), the port value must be
set in two places:

- in the inventory file, for each host, with the host var. `ansible_port`
- in the playbook or variable file with the variable `ssh_port`

## Playbook execution examples

```bash
# To deploy community Postgres version 14.6
ansible-playbook playbook.yml \
  -i inventory.yml \
  -u <ssh-user> \
  --private-key <ssh-private-key> \
  --extra-vars="pg_version=14.6 pg_type=PG"
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

## Tmax OpenSQL Version
Tmax OpenSQL v2.0

## License

BSD

## Author information

Authors:

- [Sung Woo Chang](https://github.com/dbxpert)
- [Sang Myeung Lee](https://github.com/sungmu1)
