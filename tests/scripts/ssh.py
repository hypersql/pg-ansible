# coding: utf-8

import os
import common
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def build_ssh_config(ssh_dir, name="ssh_config"):
    common.Logger().info("Building ssh config")
    ssh_config = """
Host *
    StrictHostKeyChecking no
    """
    with open(os.path.join(ssh_dir, name), "w") as f:
        f.write(ssh_config)
    os.chmod(os.path.join(ssh_dir, name), 0o600)

def ssh_keygen(ssh_dir):
    key = rsa.generate_private_key(
        backend=default_backend(), public_exponent=65537, key_size=2048
    )
    b_private_key = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    )
    common.Logger().debug(f"SSH private key: {b_private_key}")

    b_public_key = key.public_key().public_bytes(
        serialization.Encoding.OpenSSH, serialization.PublicFormat.OpenSSH
    )
    common.Logger().debug(f"SSH public key: {b_public_key}")

    ssh_private_key_file_path = os.path.join(ssh_dir, common.SSH_PRIVATE_KEY_FILE)
    with open(ssh_private_key_file_path, "wb") as f:
        f.write(b_private_key)

    ssh_public_key_file_path = os.path.join(ssh_dir, common.SSH_PUBLIC_KEY_FILE)
    with open(ssh_public_key_file_path, "wb") as f:
        f.write(b_public_key + b"\n")

    build_ssh_config(ssh_dir)