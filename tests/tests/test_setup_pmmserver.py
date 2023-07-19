import pytest
from conftest import get_pg_version, get_pmmserver, load_ansible_vars


def test_setup_pmmserver_PG():
    host = get_pmmserver()[0]

    inventory_data = load_inventory()
    container_name = inventory_data["all"]["pmmserver"][0]

    #TODO: Check the docker container to see if the pmm server is properly serviced in docker
    assert host.docker(container_name).is_running, "pmmserver docker container not running"


def test_pmm_http_service():
    ansible_vars = load_ansible_vars()
    host = get_pmmserver()[0]
    pmm_server_port = ansible_vars["pmm_server_port"]
    docker_socket_dir = ""
