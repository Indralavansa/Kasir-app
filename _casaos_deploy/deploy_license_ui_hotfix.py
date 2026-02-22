#!/usr/bin/env python3
"""Hotfix deploy for license_server UI templates to CasaOS.

Uploads updated admin templates and copies them into the existing container,
then starts/restarts the container.
"""

import os
import socket
import time

import paramiko

REMOTE_HOST = os.environ.get("CASAOS_HOST", "192.168.1.25")
REMOTE_USER = os.environ.get("CASAOS_USER", "root")
REMOTE_PASS = os.environ.get("CASAOS_PASS", "goodlife")
REMOTE_ROOT = os.environ.get("LICENSE_SERVER_REMOTE_ROOT", "/DATA/AppData/kasir-license-server")

LOCAL_LOGIN = r"d:\connect casa os\license_server\templates\admin\login.html"
LOCAL_DASH = r"d:\connect casa os\license_server\templates\admin\dashboard.html"


def _wait_exit_status(channel: paramiko.Channel, timeout_s: int) -> int | None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if channel.exit_status_ready():
            return channel.recv_exit_status()
        time.sleep(0.2)
    return None


def _run_remote(ssh: paramiko.SSHClient, command: str, timeout_s: int) -> tuple[int | None, str, str]:
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_code = _wait_exit_status(stdout.channel, timeout_s=timeout_s)

    try:
        out_text = stdout.read().decode('utf-8', errors='replace')
    except (socket.timeout, TimeoutError, paramiko.buffered_pipe.PipeTimeout):
        out_text = ""
    except Exception:
        out_text = ""

    try:
        err_text = stderr.read().decode('utf-8', errors='replace')
    except (socket.timeout, TimeoutError, paramiko.buffered_pipe.PipeTimeout):
        err_text = ""
    except Exception:
        err_text = ""

    return exit_code, out_text, err_text


def main() -> None:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(REMOTE_HOST, username=REMOTE_USER, password=REMOTE_PASS, timeout=30)

    print("[1] Upload templates to host...")
    sftp = ssh.open_sftp()
    try:
        _run_remote(ssh, f"mkdir -p {REMOTE_ROOT}/templates/admin", timeout_s=10)
        sftp.put(LOCAL_LOGIN, f"{REMOTE_ROOT}/templates/admin/login.html")
        sftp.put(LOCAL_DASH, f"{REMOTE_ROOT}/templates/admin/dashboard.html")
    finally:
        sftp.close()

    print("[2] Find license container...")
    exit_code, out, err = _run_remote(
        ssh,
        "docker ps -a --format '{{.Names}}' | grep -i license | head -n 1 || true",
        timeout_s=10,
    )
    name = (out or "").strip()
    if not name:
        print("[ERROR] No license container found")
        ssh.close()
        return
    print("    Container:", name)

    print("[3] Copy templates into container...")
    _run_remote(ssh, f"docker cp {REMOTE_ROOT}/templates/admin/login.html {name}:/app/templates/admin/login.html", timeout_s=30)
    _run_remote(ssh, f"docker cp {REMOTE_ROOT}/templates/admin/dashboard.html {name}:/app/templates/admin/dashboard.html", timeout_s=30)

    print("[4] Start/restart container...")
    # If stopped, start; if running, restart
    _run_remote(ssh, f"docker restart {name} || docker start {name}", timeout_s=60)

    print("[5] Status...")
    exit_code, out, err = _run_remote(ssh, f"docker ps --format '{{.Names}}\t{{.Status}}' | grep -i license || true", timeout_s=10)
    if out.strip():
        print(out.strip())

    ssh.close()
    print("\nOpen: http://%s:8088/admin" % REMOTE_HOST)


if __name__ == '__main__':
    main()
