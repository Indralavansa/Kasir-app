#!/usr/bin/env python3
"""Create a license key on the CasaOS-hosted license server (writes to its SQLite DB).

This runs `admin_create_license.py` inside the `kasir-license-server` container.

Env (optional):
- CASAOS_HOST (default 192.168.1.25)
- CASAOS_USER (default root)
- CASAOS_PASS (default goodlife)
- LICENSE_SERVER_CONTAINER (default kasir-license-server)

Usage:
  python create_license_on_casaos.py trial --days 30
  python create_license_on_casaos.py standard
  python create_license_on_casaos.py pro
  python create_license_on_casaos.py unlimited
"""

import argparse
import socket
import time

import paramiko


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
    import os

    host = os.environ.get('CASAOS_HOST', '192.168.1.25')
    user = os.environ.get('CASAOS_USER', 'root')
    password = os.environ.get('CASAOS_PASS', 'goodlife')
    container = os.environ.get('LICENSE_SERVER_CONTAINER', 'kasir-license-server')

    p = argparse.ArgumentParser()
    p.add_argument('tier', choices=['trial', 'standard', 'pro', 'unlimited'])
    p.add_argument('--days', type=int, default=30)
    args = p.parse_args()

    cmd = f"docker exec {container} python admin_create_license.py {args.tier}"
    if args.tier == 'trial':
        cmd += f" --days {int(args.days)}"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=20)

    exit_code, out_text, err_text = _run_remote(ssh, cmd, timeout_s=60)
    ssh.close()

    if out_text.strip():
        print(out_text.strip())
    if err_text.strip():
        print(err_text.strip())

    if exit_code not in (0, None):
        raise SystemExit(f"Failed (exit={exit_code})")


if __name__ == '__main__':
    main()
