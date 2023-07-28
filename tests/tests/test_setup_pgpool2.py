import pytest
from conftest import get_pg_version, get_pgpool2, get_primary, load_ansible_vars


def test_setup_pgpool2_PG():
    ansible_vars = load_ansible_vars()
    host = get_pgpool2()[0]
    service = "pgpool-II"
    use_system_user = ansible_vars["use_system_user"]

    if use_system_user:
        assert host.service(service).is_running, "pgpool2 service not running"

        assert host.service(service).is_enabled, "pgpool2 service not enabled"
    elif not use_system_user:
        pid_file_path = "/var/run/pgpool-II/pgpool.pid"
        pgpool_pid = host.file("%s" % pid_file_path).content_string.split()
        pgpool_pid[0] = pgpool_pid[0].replace("\x00", "")

        assert len(host.process.filter(pid=pgpool_pid[0])) > 0, "pgpool2 process not running"


def test_setup_pgpool_PG_packages():
    host = get_pgpool2()[0]
    pg_version = get_pg_version()
    packages = ["pgpool-II-pg%s" % pg_version, "openssl"]

    for package in packages:
        assert host.package(package).is_installed, "Package %s not installed" % packages


def test_setup_pgpool_test_user():
    ansible_vars = load_ansible_vars()
    pgpool2_user = ansible_vars["pgpool2_users"][0]["name"]
    pgpool2_password = ansible_vars["pgpool2_users"][0]["pass"]
    pgpool2_port = ansible_vars["pgpool2_port"]

    pg_user = "postgres"

    pgpool2_address = get_pgpool2()[0]
    address = str(pgpool2_address).strip("<>").split("//")[1]
    host = get_primary()

    with host.sudo(pg_user):
        query = "Select * from pg_user where usename = '%s'" % pgpool2_user
        cmd = host.run(
            'PGPASSWORD=%s psql -At -U %s -h %s -p %s -c "%s" postgres'
            % (pgpool2_password, pgpool2_user, address, pgpool2_port, query)
        )
        result = cmd.stdout.strip()

    assert len(result) > 0, "pgpool test user was not created sucessfully."


def test_setup_pgpool_users():
    ansible_vars = load_ansible_vars()
    pgpool2_user = ansible_vars["pgpool2_users"][0]["name"]
    pgpool2_password = ansible_vars["pgpool2_users"][0]["pass"]
    pgpool2_port = ansible_vars["pgpool2_port"]

    pg_user = "postgres"

    pgpool2_address = get_pgpool2()[0]
    address = str(pgpool2_address).strip("<>").split("//")[1]
    host = get_primary()

    with host.sudo(pg_user):
        query = "Select usename from pg_user where usename = '%s'" % (
            "pgpool2",
        )
        cmd = host.run(
            'PGPASSWORD=%s psql -At -U %s -h %s -p %s -c "%s" postgres'
            % (pgpool2_password, pgpool2_user, address, pgpool2_port, query)
        )
        result = cmd.stdout.strip().split("\n")

    assert len(result) == 1, "pgpool users was not created sucessfully."


def test_setup_pgpool_loadbalance():
    ansible_vars = load_ansible_vars()
    pgpool2_user = ansible_vars["pgpool2_users"][0]["name"]
    pgpool2_password = ansible_vars["pgpool2_users"][0]["pass"]
    pgpool2_port = ansible_vars["pgpool2_port"]

    pg_user = "postgres"

    pgpool2_address = get_pgpool2()[0]
    address = str(pgpool2_address).strip("<>").split("//")[1]
    host = get_primary()

    with host.sudo(pg_user):
        query = "PGPOOL SHOW load_balance_mode;"
        cmd = host.run(
            "PGPASSWORD=%s psql -At -U %s -h %s -p %s -c '%s' postgres"
            % (pgpool2_password, pgpool2_user, address, pgpool2_port, query)
        )
        result = cmd.stdout.strip()

    assert result == "on", "Load Balance is not enabled."

def test_setup_pgpool_watchdog():
    ansible_vars = load_ansible_vars()
    pgpool2_user = ansible_vars["pgpool2_users"][0]["name"]
    pgpool2_password = ansible_vars["pgpool2_users"][0]["pass"]
    pgpool2_port = ansible_vars["pgpool2_port"]

    pg_user = "postgres"

    pgpool2_address = get_pgpool2()[0]
    address = str(pgpool2_address).strip("<>").split("//")[1]
    host = get_primary()

    with host.sudo(pg_user):
        query = "PGPOOL SHOW use_watchdog;"
        cmd = host.run(
            "PGPASSWORD=%s psql -At -U %s -h %s -p %s -c '%s' postgres"
            % (pgpool2_password, pgpool2_user, address, pgpool2_port, query)
        )
        result = cmd.stdout.strip()

    assert result == "on", "Watchdog is not enabled."
