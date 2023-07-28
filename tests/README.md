# OpenSQL Ansible Collection Test Framework
This is a test framework for OpenSQL ansible collection.

## Authors
- [Sung Woo Chang](https://github.com/dbxpert)

## Prerequisites

This testing framework requires the following commands/tools:
- `python3`
- `pip3`
- `docker`

To install the dependencies:
```shell
pip3 install -r requirements.txt
```

## Configuration
In order for the test framework to find the Ansible project home, it needs an env variable PG_ANSIBLE_HOME set.
Use the following command to auto-configure:
```shell
cd [pg-ansible home directory]
. .env `pwd`
```

## Running Test
Use the following command to see the options for the test framework:
```shell
cd $PG_ANSIBLE_HOME/tests
python3 scripts/test-runner.py --help
```

## Usage Examples
### First Run
If it is your first time running the test framework, you need to deploy ansible collection tar ball for the test.
Use the following option to initialize the ansible collection tar ball:
```shell
python3 scripts/test-runner.py --build-ansible-tarball ...
```
### Run One Scenario
The example below shows how to run a test for:
- the `install_dbserver` test case
- on `centos7` operating systems
- for versions `14.5`

```shell
python3 scripts/test-runner.py -k install_dbserver -o centos7 -v 14.5
```
### Run Multiple Scenarios
The example below show how to run multiple tests for:
- the `setup_repo` and `init_dbserver` test cases
- on `centos7`, `rocky7` and `oraclelinux7` operating systems
- for versions `14.6`, `14.7` and `14.8`
```shell
python3 scripts/test-runner.py -k setup_repo init_dbserver \
                               -o centos7 rocky7 oraclelinux 7 \
                               -v 14.6 14.7 14.8
```

### Logs
When a test starts running, there will be stdouts with colors telling you which log file to look at for each test case.
For instance, if you run the following test scenarios,
```shell
python3 scripts/test-runner.py -k setup_repo init_dbserver -o centos7 centos8 -v 14.6 14.7 14.8 -j 12
```
You will see something like the following:
```shell
[PID=322046] Testing...(case=setup_repo, pg_version=14.8, os_type=centos8)
[PID=322046] Logs are written in /hdd/developer-env/volumes/workspace/pg-ansible/tests/.logs/setup_repo_centos8_PG14.8.stdout
[PID=322042] Testing...(case=setup_repo, pg_version=14.7, os_type=centos7)
[PID=322042] Logs are written in /hdd/developer-env/volumes/workspace/pg-ansible/tests/.logs/setup_repo_centos7_PG14.7.stdout
[PID=322047] Testing...(case=init_dbserver, pg_version=14.6, os_type=centos7)
[PID=322047] Logs are written in /hdd/developer-env/volumes/workspace/pg-ansible/tests/.logs/init_dbserver_centos7_PG14.6.stdout
[PID=322045] Testing...(case=setup_repo, pg_version=14.7, os_type=centos8)
[PID=322045] Logs are written in /hdd/developer-env/volumes/workspace/pg-ansible/tests/.logs/setup_repo_centos8_PG14.7.stdout
[PID=322051] Testing...(case=init_dbserver, pg_version=14.7, os_type=centos8)
[PID=322051] Logs are written in /hdd/developer-env/volumes/workspace/pg-ansible/tests/.logs/init_dbserver_centos8_PG14.7.stdout
[PID=322050] Testing...(case=init_dbserver, pg_version=14.6, os_type=centos8)
[PID=322050] Logs are written in /hdd/developer-env/volumes/workspace/pg-ansible/tests/.logs/init_dbserver_centos8_PG14.6.stdout
[PID=322049] Testing...(case=init_dbserver, pg_version=14.8, os_type=centos7)
[PID=322048] Testing...(case=init_dbserver, pg_version=14.7, os_type=centos7)
[PID=322049] Logs are written in /hdd/developer-env/volumes/workspace/pg-ansible/tests/.logs/init_dbserver_centos7_PG14.8.stdout
[PID=322048] Logs are written in /hdd/developer-env/volumes/workspace/pg-ansible/tests/.logs/init_dbserver_centos7_PG14.7.stdout
[PID=322044] Testing...(case=setup_repo, pg_version=14.6, os_type=centos8)
[PID=322044] Logs are written in /hdd/developer-env/volumes/workspace/pg-ansible/tests/.logs/setup_repo_centos8_PG14.6.stdout
[PID=322041] Testing...(case=setup_repo, pg_version=14.6, os_type=centos7)
[PID=322041] Logs are written in /hdd/developer-env/volumes/workspace/pg-ansible/tests/.logs/setup_repo_centos7_PG14.6.stdout
[PID=322043] Testing...(case=setup_repo, pg_version=14.8, os_type=centos7)
[PID=322043] Logs are written in /hdd/developer-env/volumes/workspace/pg-ansible/tests/.logs/setup_repo_centos7_PG14.8.stdout
[PID=322052] Testing...(case=init_dbserver, pg_version=14.8, os_type=centos8)
[PID=322052] Logs are written in /hdd/developer-env/volumes/workspace/pg-ansible/tests/.logs/init_dbserver_centos8_PG14.8.stdout
```
Choose and tail the log file to see the current progress of the ansible controller:
```shell
tail -f /hdd/developer-env/volumes/workspace/pg-ansible/tests/.logs/init_dbserver_centos8_PG14.8.stdout
```

### Debugging
After runnging tests, the docker containers that are created will be removed automatically.
If you would like to maintain the containers so that you can do debugging, use the following option:
```shell
python3 scripts/test-runner.py -m ...
```
This will ensure the containers survive even after test failures.
After debugging, you will want to clean all the docker containers. Use the following option for that:
```shell
python3 scripts/test-runner.py -r ...
```
This will remove all the docker containers that were created by the test runners (DO NOT MANUALLY REMOVE CONTESTS IN ./.cidfiles)
