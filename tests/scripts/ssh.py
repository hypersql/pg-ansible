# coding: utf-8

import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

SSH_PRIVATE_KEY_FILE="id_rsa"
SSH_PUBLIC_KEY_FILE="id_rsa.pub"

def build_ssh_config(ssh_dir, name="ssh_config"):
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

    b_public_key = key.public_key().public_bytes(
        serialization.Encoding.OpenSSH, serialization.PublicFormat.OpenSSH
    )

    ssh_private_key_file_path = os.path.join(ssh_dir, SSH_PRIVATE_KEY_FILE)
    with open(ssh_private_key_file_path, "wb") as f:
        f.write(b_private_key)

    ssh_public_key_file_path = os.path.join(ssh_dir, SSH_PUBLIC_KEY_FILE)
    with open(ssh_public_key_file_path, "wb") as f:
        f.write(b_public_key + b"\n")

    build_ssh_config(ssh_dir)