from conftest import get_pgpool2, get_primary, load_ansible_vars


def test_manage_pgpool_pcp_user():
    ansible_vars = load_ansible_vars()
    pcp_user = ansible_vars["pcp_users"][0]["name"]
    pcp_pass = ansible_vars["pcp_users"][0]["pass"]
    pg_user = "postgres"

    host = get_pgpool2()[0]

    with host.sudo(pg_user):
        cmd = host.run("touch ~/.pcppass")
        cmd = host.run(
            "echo 'localhost:9898:%s:%s' >> ~/.pcppass" % (pcp_user, pcp_pass)
        )
        cmd = host.run("chmod 600 ~/.pcppass ")
        cmd = host.run("pcp_node_info -U %s -h localhost -w" % pcp_user)
        result = cmd.stdout.strip()

    assert len(result) > 0, "pcp command succesfully works"


def test_manage_pgpool_pcp_node_count():
    ansible_vars = load_ansible_vars()
    pcp_user = ansible_vars["pcp_users"][0]["name"]
    pg_user = "postgres"

    host = get_pgpool2()[0]

    with host.sudo(pg_user):
        cmd = host.run("pcp_node_count -U %s -h localhost -w" % pcp_user)
        result = cmd.stdout.strip()

    assert result == "1", "Database node count is not equal to 1"


def test_manage_pgpool_test_user():
    ansible_vars = load_ansible_vars()
    pgpool2_user = ansible_vars["pgpool2_users"][0]["name"]
    pgpool2_password = ansible_vars["pgpool2_users"][0]["pass"]
    pgpool2_port = ansible_vars["pgpool2_port"]

    pg_user = "postgres"

    pgpool2_address = get_pgpool2()[0]
    address = str(pgpool2_address).strip("<>").split("//")[1]
    host = get_primary()

    with host.sudo(pg_user):
        query = "Select usename from pg_user where usename = '%s'" % pgpool2_user
        cmd = host.run(
            'PGPASSWORD=%s psql -At -U %s -h %s -p %s -c "%s" postgres'
            % (pgpool2_password, pgpool2_user, address, pgpool2_port, query)
        )
        result = cmd.stdout.strip().split("\n")

    assert len(result) == 1, "test user was not created sucessfully."


def test_manage_pgpool_pcp_socket():
    ansible_vars = load_ansible_vars()
    pgpool2_user = ansible_vars["pgpool2_users"][0]["name"]
    pgpool2_password = ansible_vars["pgpool2_users"][0]["pass"]
    pgpool2_port = ansible_vars["pgpool2_port"]

    pg_user = "postgres"

    pgpool2_address = get_pgpool2()[0]
    address = str(pgpool2_address).strip("<>").split("//")[1]
    host = get_primary()

    with host.sudo(pg_user):
        query = "PGPOOL SHOW pcp_socket_dir;"
        cmd = host.run(
            "PGPASSWORD=%s psql -At -U %s -h %s -p %s -c '%s' postgres"
            % (pgpool2_password, pgpool2_user, address, pgpool2_port, query)
        )
        result = cmd.stdout.strip()

    assert result == "/tmp", "Load Balance is not enabled."
