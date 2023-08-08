#!/bin/bash -eux
mkdir -p /root/.ssh
chmod 0700 /root/.ssh
cp "/workspace/.ssh/id_rsa" /root/.ssh/.
cp "/workspace/.ssh/ssh_config" /root/.ssh/.
chmod 0600 /root/.ssh/id_rsa

my_ansible_files_prefix="${OPENSQL_CASE_NAME}_${OPENSQL_OS_TYPE}_PG${OPENSQL_PG_VERSION}"
"/workspace/.inventory/${my_ansible_files_prefix}.add_hosts.sh"

export ANSIBLE_CONFIG=/workspace/docker/ansible.cfg
export OPENSQL_SSH_USER=root
export OPENSQL_SSH_KEY=/root/.ssh/id_rsa
export OPENSQL_SSH_CONFIG=/root/.ssh/ssh_config
export OPENSQL_INVENTORY="/workspace/.inventory/${my_ansible_files_prefix}.inventory.yml"
export OPENSQL_ANSIBLE_VARS="/workspace/cases/${OPENSQL_CASE_NAME}/vars.json"
export PLAYBOOK_NAME="playbook.yml"
if ${PRE_BUILD:-false} ; then
	export PLAYBOOK_NAME="pre_image_playbook.yml"
fi

ansible-playbook \
	-i "${OPENSQL_INVENTORY}" \
	--extra-vars "pg_type='PG'" \
	--extra-vars "pg_version=${OPENSQL_PG_VERSION}" \
	--extra-vars "@${OPENSQL_ANSIBLE_VARS}" \
	--private-key ${OPENSQL_SSH_KEY} \
	"/workspace/cases/${OPENSQL_CASE_NAME}/${PLAYBOOK_NAME}"

py.test -v -k "${OPENSQL_CASE_NAME}" /workspace/tests
