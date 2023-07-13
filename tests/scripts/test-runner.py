#!env python3
# encoding: utf-8

import argparse
import os
import shlex
import subprocess
import termcolor
import yaml
import logging
from multiprocessing import Pool
from pathlib import Path
from ssh import ssh_keygen, SSH_PUBLIC_KEY_FILE
from docker import DockerContainer
from jinja2 import Environment, FileSystemLoader

def get_ansible_project_home():
    return os.environ['PG_ANSIBLE_HOME']

def get_ansible_test_home():
    return os.path.join(get_ansible_project_home(), "tests")

SSH_DIR = os.path.join(get_ansible_test_home(), ".ssh")
LOG_DIR = os.path.join(get_ansible_test_home(), ".logs")
CIDFILE_DIR = os.path.join(get_ansible_test_home(), ".cidfiles")
INVENTORY_DIR = os.path.join(get_ansible_test_home(), ".inventory")

logging.WARNING

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class ColoredPrinter(metaclass=Singleton):
    def __init__(self):
        self.colors = ["red", "green", "yellow", "blue", "magenta", "cyan"]
        self.pid = os.getpid()
        self.my_color = self.colors[self.pid % len(self.colors)]

    def print_message(self, message):
        text = termcolor.colored(f"[PID={self.pid}] " + message, self.my_color)
        print(text)

class TestConfiguration(metaclass=Singleton):
    def __init__(self):
        config_path = "test-config.yml"
        with open(config_path, "r") as config_file:
            self.config = yaml.load(config_file, Loader=yaml.BaseLoader)

    def __getitem__(self, item):
        return self.config[item]

class PgVersionChecker(argparse.Action):
    def __init__(self, option_strings, *args, **kwargs):
        config = TestConfiguration()
        self.available_versions = config["available_pg_versions"]
        super(PgVersionChecker, self).__init__(option_strings, *args, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        for v in values:
            if v not in self.available_versions:
                parser.error("Postgres version %s not supported" % v)
        setattr(namespace, self.dest, values)

class OSChecker(argparse.Action):
    def __init__(self, option_strings, *args, **kwargs):
        config = TestConfiguration()
        self.available_os_types = config["available_os_types"]
        super(OSChecker, self).__init__(option_strings, *args, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        for v in values:
            if v not in self.available_os_types:
                parser.error("Operating system %s not supported" % v)
        setattr(namespace, self.dest, values)

def run_command_line(command):
    c = shlex.split(command)
    r = subprocess.run(c, capture_output=True)
    if r.returncode != 0:
        raise Exception(r.stderr.decode("utf-8"))

    return r

def main():
    args = get_input_arguments()

    if args.remove_containers:
        remove_all_containers()
        quit()

    if not validate_testing_roles(args.keywords):
        quit()

    if args.build_ansible_tarball:
        make_ansible_collection_tar_ball()
        build_ansible_tester_docker_image()

    make_log_dir()
    make_cidfile_dir()
    make_ssh_key()
    make_inventory_dir()

    args_for_exec_test = get_args_for_exec_test(args)

    for os_type in args.os_types:
        build_docker_image_if_not_exist(os_type)

    with Pool(args.jobs) as p:
        p.starmap(exec_test, args_for_exec_test)

def get_input_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-j",
        "--jobs",
        dest="jobs",
        type=int,
        help="Number of parallel jobs. Default: %(default)s",
        default=4,
    )

    parser.add_argument(
        "-v",
        "--pg-versions",
        dest="pg_versions",
        nargs="+",
        default=["14.6"],
        action=PgVersionChecker,
        help="Postgres versions list. Default: %(default)s",
    )

    parser.add_argument(
        "-o",
        "--os-types",
        dest="os_types",
        nargs="+",
        default=["centos7"],
        action=OSChecker,
        help="Operating systems list. Default: %(default)s",
    )

    parser.add_argument(
        "-k",
        "--keywords",
        dest="keywords",
        nargs="+",
        default=[""],
        help="Execute test cases with a name matching the given keywords.",
    )

    parser.add_argument(
        "-b",
        "--build-ansible-tarball",
        dest="build_ansible_tarball",
        action="store_true",
        help="Update the ansible collection with a new tar ball.",
    )

    parser.add_argument(
        "-m",
        "--maintain-containers",
        dest="maintain_containers",
        action="store_true",
        help="Maintain containers after the test is complete",
    )

    parser.add_argument(
        "-r",
        "--remove-containers",
        dest="remove_containers",
        action="store_true",
        help="Remove all containers created from this test.",
    )

    return parser.parse_args()

def remove_all_containers():
    if not Path(CIDFILE_DIR).exists():
        return
    for cidfile_name in os.listdir(CIDFILE_DIR):
        remove_container_with_cid(cidfile_name)
        remove_cidfile(cidfile_name)
        print(f"Container {cidfile_name} is removed")

def get_cid_from_cidfile(cidfile_name):
    cidfile_path = os.path.join(CIDFILE_DIR, cidfile_name)
    cid = ""
    with open(cidfile_path) as cidfile:
        cid = cidfile.readline()

    return cid

def remove_container_with_cid(cidfile_name):
    cid = get_cid_from_cidfile(cidfile_name)
    run_command_line(f"docker rm -f {cid}")

def remove_cidfile(cidfile_name):
    cidfile_path = os.path.join(CIDFILE_DIR, cidfile_name)
    if os.path.isfile(cidfile_path):
        os.remove(cidfile_path)

def validate_testing_roles(keywords):
    for keyword in keywords:
        if keyword not in TestConfiguration()["available_roles"]:
            print(f"No roles with name {keyword}")
            return False
    return True

def make_ansible_collection_tar_ball():
    project_home = get_ansible_project_home()
    run_command_line(f"make -C {project_home} clean_for_test build_for_test")

def build_ansible_tester_docker_image():
    docker_dir = os.path.join(get_ansible_test_home(), "docker")
    run_command_line(f"docker build -f {docker_dir}/Dockerfile.ansible-tester -t opensql-test-controller {docker_dir}")

def make_log_dir():
    make_dir(LOG_DIR)

def make_cidfile_dir():
    make_dir(CIDFILE_DIR)

def make_ssh_key():
    if not Path(SSH_DIR).exists():
        os.mkdir(SSH_DIR, mode=755)
        ssh_keygen(SSH_DIR)

def make_inventory_dir():
    make_dir(INVENTORY_DIR)

def make_dir(path):
    if not Path(path).exists():
        os.mkdir(path, mode=755)

def get_args_for_exec_test(args):
    test_args = []
    for role in args.keywords:
        for os_type in args.os_types:
            for pg_version in args.pg_versions:
                test_args.append(
                    (role, os_type, pg_version, args.maintain_containers)
                )
    return test_args

def build_docker_image_if_not_exist(os_type):
    r = run_command_line(f"docker images --filter=reference='opensql-test-{os_type}' --format '{{.ID}}'")
    if len(r.stdout) == 0:
        print(f"Docker image opensql-test-{os_type} doesn't exist. Creating one...")
        docker_dir = os.path.join(get_ansible_test_home(), "docker")
        run_command_line(f"docker build -f {docker_dir}/Dockerfile.{os_type} -t opensql-test-{os_type} {docker_dir}")

def exec_test(case_name, os_type, pg_version, maintain_containers):
    printer = ColoredPrinter()
    message = f"Testing...(case={case_name}, pg_version={pg_version}, os_type={os_type})"
    printer.print_message(message)

    hostnames = get_inventory_hostnames_for_test_case(case_name)
    create_managed_docker_containers(case_name, os_type, pg_version, hostnames)
    create_ansible_tester_container(case_name, os_type, pg_version, hostnames)

    if not maintain_containers:
        tear_down(case_name, os_type, pg_version)

def get_inventory_hostnames_for_test_case(case_name):
    hostnames = ["primary1"]

    if case_name == "common_arch":
        hostnames.append("standby1")
        hostnames.append("standby2")
        hostnames.append("pool1")
        hostnames.append("barman1")

    if case_name == "manage_barmanbackup":
        hostnames.append("barman1")

    if case_name == "manage_pgbouncer":
        hostnames.append("pooler1")

    if case_name == "manage_pgpool2":
        hostnames.append("pool1")

    if case_name == "setup_barmanserver":
        hostnames.append("barman1")

    if case_name == "setup_pgbouncer":
        hostnames.append("pooler1")

    if case_name == "setup_pgpool2":
        hostnames.append("standby1")
        hostnames.append("standby2")
        hostnames.append("pool1")
        hostnames.append("pool2")
        hostnames.append("pool3")

    if case_name == "setup_replication":
        hostnames.append("standby1")
        hostnames.append("standby2")

    if case_name == "setup_repmgr":
        hostnames.append("standby1")
        hostnames.append("witness1")

    return hostnames

def create_managed_docker_containers(case_name, os_type, pg_version, hostnames):
    for hostname in hostnames:
        ctnr_name = get_container_name(case_name, os_type, pg_version, hostname)
        run_command_line(get_managed_docker_ctnr_run_command(ctnr_name, os_type))
        setup_ssh_configuration(ctnr_name)

def get_container_name(case_name, os_type, pg_version, hostname):
    return f"{get_container_name_prefix(case_name, os_type, pg_version)}_{hostname}"

def get_container_name_prefix(case_name, os_type, pg_version):
    return f"{case_name}_{os_type}_PG{pg_version}"

def get_managed_docker_ctnr_run_command(ctnr_name, os_type):
    docker_command = f"docker run -d --cidfile {CIDFILE_DIR}/{ctnr_name} "
    docker_command += "--cap-add SYS_ADMIN "
    # rw mode is okay with cgroup v2, but might be troublesome with cgroup v1
    docker_command += "--volume /sys/fs/cgroup/:/sys/fs/cgroup:rw "
    docker_command += f"--name {ctnr_name} "
    docker_command += f"opensql-test-{os_type} "
    docker_command += "/usr/sbin/init"
    return docker_command

def setup_ssh_configuration(ctnr_name):
    cid = get_cid_from_cidfile(ctnr_name)
    docker_ctnr = DockerContainer(cid)
    docker_ctnr.setup_ssh_server()
    docker_ctnr.rm("/root/.ssh")
    docker_ctnr.mkdir("/root/.ssh", mode="0700")
    docker_ctnr.add_ssh_pub_key(f"{SSH_DIR}/{SSH_PUBLIC_KEY_FILE}")

def create_ansible_tester_container(case_name, os_type, pg_version, hostnames):
    build_inventory(case_name, os_type, pg_version, hostnames)
    build_add_hosts(case_name, os_type, pg_version, hostnames)

    printer = ColoredPrinter()

    command = get_ansible_tester_docker_ctnr_run_command(case_name, os_type, pg_version)
    command = shlex.split(command)
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        close_fds=True,
    )

    stdout_logfile_name = f"{LOG_DIR}/{case_name}_{os_type}_PG{pg_version}.stdout"
    stdout_logfile = open(stdout_logfile_name, "wb", buffering=0)
    printer.print_message(f"Logs are written in {stdout_logfile_name}")

    while process.poll() is None:
        line = process.stdout.readline()
        stdout_logfile.write(line)

    stdout_logfile.close()
    exitcode = process.wait()

    result_message = "Success" if exitcode == 0 else "Fail"

    printer = ColoredPrinter()
    printer.print_message(
        f"Test Complete...({case_name}, {pg_version}, {os_type}) with result: {result_message}"
    )


def build_inventory(case_name, os_type, pg_version, hostnames):
    inventory_vars = {}
    for hostname in hostnames:
        cidfile = get_container_name(case_name, os_type, pg_version, hostname)
        cid = get_cid_from_cidfile(cidfile)
        container = DockerContainer(cid)
        inventory_vars[f"{hostname}_ip"] = container.ip()

    template_dir = os.path.join(get_ansible_test_home(), f"cases/{case_name}")
    file_loader = FileSystemLoader(template_dir)
    jenv = Environment(loader=file_loader, trim_blocks=True)
    template = jenv.get_template("inventory.yml.j2")

    inventory_file_name = get_container_name_prefix(case_name, os_type, pg_version)
    inventory_path = os.path.join(INVENTORY_DIR, f"{inventory_file_name}.inventory.yml")
    with open(inventory_path, "w") as f:
        f.write(template.render(inventory_vars=inventory_vars))

def build_add_hosts(case_name, os_type, pg_version, hostnames):
    add_hosts_script_name = get_container_name_prefix(case_name, os_type, pg_version)
    add_hosts_script_path = os.path.join(INVENTORY_DIR, f"{add_hosts_script_name}.add_hosts.sh")

    with open(add_hosts_script_path, "w") as f:
        f.write("#!/bin/bash\n")
        for hostname in hostnames:
            cidfile = get_container_name(case_name, os_type, pg_version, hostname)
            cid = get_cid_from_cidfile(cidfile)
            container = DockerContainer(cid)
            f.write(f"ssh-keyscan -H {container.ip()} >> ~/.ssh/known_hosts\n")

    os.chmod(add_hosts_script_path, 0o755)

def get_ansible_tester_docker_ctnr_run_command(case_name, os_type, pg_version):
    ctnr_name = f"{get_container_name_prefix(case_name, os_type, pg_version)}_ansible_tester"
    docker_command = f"docker run --cidfile {CIDFILE_DIR}/{ctnr_name} "
    docker_command += f"--volume {get_ansible_test_home()}:/workspace "
    docker_command += f"--name {ctnr_name} "
    docker_command += f"-e OPENSQL_CASE_NAME={case_name} "
    docker_command += f"-e OPENSQL_OS_TYPE={os_type} "
    docker_command += f"-e OPENSQL_PG_VERSION={pg_version} "
    docker_command += "opensql-test-controller "
    docker_command += "/workspace/docker/exec-tests.sh"
    return docker_command

def tear_down(case_name, os_type, pg_version):
    cidfile_prefix = get_container_name_prefix(case_name, os_type, pg_version)
    for cidfile_name in os.listdir(CIDFILE_DIR):
        if cidfile_name.startswith(cidfile_prefix):
            remove_container_with_cid(cidfile_name)
            remove_cidfile(cidfile_name)

if __name__ == "__main__":
    main()
