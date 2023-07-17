from conftest import (
    get_pg_type,
    get_pgbouncer,
    get_primary,
    load_ansible_vars,
    os_family,
)


def test_setup_pgbouncer_service():
    ansible_vars = load_ansible_vars()
    host = get_pgbouncer()[0]
    service = "pgbouncer"
    use_system_user = ansible_vars["use_system_user"]

    if use_system_user:
        assert host.service(service).is_running, "pgbouncer service not running"

        assert host.service(service).is_enabled, "pgbouncer service not enabled"
    elif not use_system_user:
        if os_family() == "RedHat":
            pid_file_path = "/run/pgbouncer/pgbouncer.pid"
        elif os_family() == "Debian":
            pid_file_path = "/var/run/pgbouncer/pgbouncer.pid"
        pgbouncer_pid = host.file("%s" % pid_file_path).content_string.split()

        assert len(host.process.filter(pid=pgbouncer_pid[0])) > 0, "Pgbouncer process not running"


def test_setup_pgbouncer_packages():
    host = get_pgbouncer()[0]

    packages = ["pgbouncer"]

    for package in packages:
        assert host.package(package).is_installed, "Package %s not installed" % packages


def test_setup_pgbouncer_test_user():
    ansible_vars = load_ansible_vars()
    pgbouncer_user = ansible_vars["pgbouncer_auth_user_list"][0]["username"]
    pgbouncer_password = ansible_vars["pgbouncer_auth_user_list"][0]["password"]
    pgbouncer_port = ansible_vars["pgbouncer_listen_port"]

    pg_user = "postgres"

    pgbouncer_address = get_pgbouncer()[0]
    address = str(pgbouncer_address).strip("<>").split("//")[1]
    host = get_primary()

    with host.sudo(pg_user):
        query = "SHOW users"
        cmd = host.run(
            'PGPASSWORD=%s psql -At -U %s -h %s -p %s -c "%s" pgbouncer | grep %s'
            % (
                pgbouncer_password,
                pgbouncer_user,
                address,
                pgbouncer_port,
                query,
                pgbouncer_user,
            )
        )
        result = cmd.stdout.strip()

    assert len(result) > 0, "pgbouncer test user was not created sucessfully."


def test_setup_pgbouncer_config():
    ansible_vars = load_ansible_vars()
    pgbouncer_user = ansible_vars["pgbouncer_auth_user_list"][0]["username"]
    pgbouncer_password = ansible_vars["pgbouncer_auth_user_list"][0]["password"]
    pgbouncer_port = ansible_vars["pgbouncer_listen_port"]
    pgbouncer_admin_user = ansible_vars["pgbouncer_admin_users"]

    pg_user = "postgres"

    pgbouncer_address = get_pgbouncer()[0]
    address = str(pgbouncer_address).strip("<>").split("//")[1]
    host = get_primary()

    with host.sudo(pg_user):
        query = "SHOW config"
        cmd = host.run(
            'PGPASSWORD=%s psql -At -U %s -h %s -p %s -c "%s" pgbouncer | grep %s'
            % (
                pgbouncer_password,
                pgbouncer_user,
                address,
                pgbouncer_port,
                query,
                "admin_users",
            )
        )
        result = cmd.stdout.strip()

    assert (
        pgbouncer_admin_user in result
    ), "pgbouncer admin user was not configured properly."


def test_setup_pgbouncer_port():
    ansible_vars = load_ansible_vars()
    pgbouncer_user = ansible_vars["pgbouncer_auth_user_list"][0]["username"]
    pgbouncer_password = ansible_vars["pgbouncer_auth_user_list"][0]["password"]
    pgbouncer_port = ansible_vars["pgbouncer_listen_port"]

    pg_user = "postgres"

    pgbouncer_address = get_pgbouncer()[0]
    address = str(pgbouncer_address).strip("<>").split("//")[1]
    host = get_primary()

    with host.sudo(pg_user):
        query = "SHOW active_sockets"
        cmd = host.run(
            'PGPASSWORD=%s psql -At -U %s -h %s -p %s -c "%s" pgbouncer | grep %s'
            % (
                pgbouncer_password,
                pgbouncer_user,
                address,
                pgbouncer_port,
                query,
                pgbouncer_port,
            )
        )
        result = cmd.stdout.strip()

    assert len(result) > 0, "pgbouncer port was not configured properly."
