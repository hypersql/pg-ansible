# manage_pgpool2

This role is for managing PgpoolII configuration parameters and user list.

## Requirements

Following are the dependencies and requirement of this role.

1. Ansible
2. `tmax_opensql.postgres` -> `setup_repo` role for setting the repository on
   the systems.
3. `tmax_opensql.postgres` -> `setup_pgpool2` - role for setting up PgpoolII
   on the systems.

## Role Variables

When executing the role via ansible these are the required variables:

  * ***pg_version***

  Postgres Versions supported are: `14.0`, `14.1`, `14.2`, `14.3`,`14.3`, `14.5`, `14.6`, `14.7`, `14.8`, `15.0`, `15.1`, `15.2`, `15.3`

  Database Engine supported are: `PG`

The rest of the variables can be configured and are available in the:

  * [roles/manage_pgpool2/vars/PG.yml](./vars/PG.yml)

Below is the documentation of the rest of the variables:

### pgpool2_configuration

This is the list of the configuration parameters to be changed in PgpoolII
configuration file.

Example:

```yaml
pgpool2_configuration:
  - key: "port"
    value: 6432
    state: present
  - key: "socket"
    value: "/tmp"
    # Add quotes around the value
    quoted: true
    state: present
  - key: "ssl_ca_cert"
    state: absent
```

Note: The PgpoolII parameters taking a string value must be quoted in the
configuration file, this behavior can be achieved by setting to `quoted`
attribute to `true`. Default value is `false`.

The `state` attribute defines if the parameter must be present or not in the
configuration file. Default value is `present`.

### pgpool2_users

This is the list of PgpoolII user account to managed.

Example:

```yaml
pgpool2_users:
  - name: "my_user1"
    pass: "password"
    auth: scram
  - name: "my_user2"
    pass: "password"
    auth: md5
  - name: "my_user_to_be_removed"
    state: absent
```

Two authentication methods are supported: `scram` and `md5`.

The `state` attribute defines if the user must be present or not in the
authentication file. Default value is `present`.

### pcp_users

This is the list of PgpoolII pcp user account to managed.

Example:

```yaml
pcp_users:
  - name: "my_user1"
    pass: "password"
  - name: "my_user2"
    pass: "password"
  - name: "my_user_to_be_removed"
    state: absent
```

The `state` attribute defines if the user must be present or not in the
authentication file. Default value is `present`.

### `use_system_user`

Restart pgpool-II systemd unit to apply the settings using this parameter.
If set to false, systemd unit is not used and it operates in the form of process through command.
Default: true

Example:

```yaml
use_system_user: false
```

## Dependencies

This role does not have any dependencies, but a PgpoolII instance should have
been deployed beforehand with the `setup_pgpool2` role.

## Example Playbook

### Inventory file content

Content of the `inventory.yml` file:

```yaml
---
all:
  children:
    pgpool2:
      hosts:
        pool1:
          ansible_host: xxx.xxx.xxx.xxx
          private_ip: xxx.xxx.xxx.xxx
          # Private IP address of the PG primary node
          primary_private_ip: xxx.xxx.xxx
    primary:
      hosts:
        primary1:
          ansible_host: xxx.xxx.xxx.xxx
          private_ip: xxx.xxx.xxx.xxx
```

### How to include the `manage_pgpool2` role in your Playbook

Below is an example of how to include the `manage_pgpool2` role:

```yaml
---
- hosts: pgpool2
  name: Manage PgpoolII instances
  become: true
  gather_facts: true

  collections:
    - tmax_opensql.postgres

  pre_tasks:
    - name: Initialize the user defined variables
      set_fact:
        pg_version: 14.6
        pg_type: "PG"

        pgpool2_configuration:
          - key: "port"
            value: 6432
            state: present
          - key: "socket"
            value: "/tmp"
            # Add quotes around the value
            quoted: true
            state: present
          - key: "ssl_ca_cert"
            state: absent

        pgpool2_users:
          - name: "my_user1"
            pass: "password"
            auth: scram
          - name: "my_user2"
            pass: "password"
            auth: md5
          - name: "my_user_to_be_removed"
            state: absent

  roles:
    - manage_pgpool2
```

Defining and adding variables is done in the `set_fact` of the `pre_tasks`.

All the variables are available at:

  * [roles/manage_pgpool2/defaults/main.yml](./defaults/main.yml)
  * [roles/manage_pgpool2/vars/PG.yml](./vars/PG.yml)

## Database engines supported
### Supported OS
- CentOS7
- CentOS8
- Rocky8
- Rocky9

### Supported PostgreSQL Version
- 14.0 - 14.8
- 15.0 - 15.3

## pgpool-II supported

- RedHat
  * pgpool-II : 4.3

## License

BSD

## Author information

Author:
  * [Sang Myeung Lee](https://github.com/sungmu1)

Original Author:
  * Julien Tachoires
  * Vibhor Kumar (Reviewer)
  * EDB Postgres
  * edb-devops@enterprisedb.com www.enterprisedb.com
