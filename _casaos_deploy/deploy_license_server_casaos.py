#!/usr/bin/env python3
"""Deploy license_server (activation + admin monitoring dashboard) to CasaOS host.

- Uploads license_server/ to /DATA/AppData/kasir-license-server
- Starts docker-compose service exposing :8088

Requirements on server:
- docker-compose (or docker compose)
- You must create /DATA/AppData/kasir-license-server/.env (copy from .env.example)

"""

import os
import socket
import time
import secrets

import paramiko

REMOTE_HOST = os.environ.get("CASAOS_HOST", "192.168.1.25")
REMOTE_USER = os.environ.get("CASAOS_USER", "root")
REMOTE_PASS = os.environ.get("CASAOS_PASS", "goodlife")

REMOTE_ROOT = os.environ.get("LICENSE_SERVER_REMOTE_ROOT", "/DATA/AppData/kasir-license-server")

LOCAL_ROOT = r"d:\connect casa os\license_server"

ADMIN_USER = (os.environ.get("ADMIN_USER", "") or "").strip()
ADMIN_PASS = (os.environ.get("ADMIN_PASS", "") or "").strip()
LICENSE_SIGNING_KEY_B64 = (os.environ.get("LICENSE_SIGNING_KEY_B64", "") or "").strip()
FLASK_SECRET_KEY = (os.environ.get("FLASK_SECRET_KEY", "") or "").strip() or secrets.token_hex(32)
TOKEN_TTL_DAYS = (os.environ.get("TOKEN_TTL_DAYS", "7") or "7").strip()


def _wait_exit_status(channel: paramiko.Channel, timeout_s: int) -> int | None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if channel.exit_status_ready():
            return channel.recv_exit_status()
        time.sleep(0.5)
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


def _sftp_put_dir(sftp: paramiko.SFTPClient, local_dir: str, remote_dir: str) -> None:
    # Create remote dir
    try:
        sftp.stat(remote_dir)
    except FileNotFoundError:
        sftp.mkdir(remote_dir)

    for root, dirs, files in os.walk(local_dir):
        rel = os.path.relpath(root, local_dir).replace('\\', '/')
        target_dir = remote_dir if rel == '.' else f"{remote_dir}/{rel}"
        try:
            sftp.stat(target_dir)
        except FileNotFoundError:
            # create nested
            parts = target_dir.split('/')
            cur = ''
            for p in parts:
                if not p:
                    continue
                cur = f"{cur}/{p}" if cur else p
                try:
                    sftp.stat(cur)
                except FileNotFoundError:
                    try:
                        sftp.mkdir(cur)
                    except Exception:
                        pass

        for d in dirs:
            d_path = f"{target_dir}/{d}"
            try:
                sftp.stat(d_path)
            except FileNotFoundError:
                try:
                    sftp.mkdir(d_path)
                except Exception:
                    pass

        for f in files:
            if f.endswith('.pyc') or f == '__pycache__':
                continue
            local_path = os.path.join(root, f)
            remote_path = f"{target_dir}/{f}"
            sftp.put(local_path, remote_path)


def main() -> None:
    print("\nDeploy license server + monitoring dashboard to CasaOS...\n")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(REMOTE_HOST, username=REMOTE_USER, password=REMOTE_PASS, timeout=30)

    print("[1] Ensure remote root exists")
    _run_remote(ssh, f"mkdir -p {REMOTE_ROOT}", timeout_s=20)

    print("[2] Upload license_server folder")
    sftp = ssh.open_sftp()
    try:
        _sftp_put_dir(sftp, LOCAL_ROOT, REMOTE_ROOT)
    finally:
        sftp.close()

    print("[3] Ensure data dir exists")
    _run_remote(ssh, f"mkdir -p {REMOTE_ROOT}/data", timeout_s=20)

    print("[4] Check .env")
    exit_code, out_text, err_text = _run_remote(ssh, f"test -f {REMOTE_ROOT}/.env && echo OK || echo MISSING", timeout_s=10)
    if (out_text or '').strip() != 'OK':
        if not (ADMIN_USER and ADMIN_PASS and LICENSE_SIGNING_KEY_B64):
            print("    [WARN] Remote .env is missing")
            print(f"    Create it: cp {REMOTE_ROOT}/.env.example {REMOTE_ROOT}/.env && nano {REMOTE_ROOT}/.env")
            print("    Required: LICENSE_SIGNING_KEY_B64, ADMIN_USER, ADMIN_PASS, FLASK_SECRET_KEY")
            print("    Or re-run with env vars set (ADMIN_USER, ADMIN_PASS, LICENSE_SIGNING_KEY_B64)")
            ssh.close()
            return

        print("    [OK] Remote .env missing; creating it from local env vars")
        env_text = "\n".join(
            [
                f"LICENSE_SIGNING_KEY_B64={LICENSE_SIGNING_KEY_B64}",
                f"LICENSE_DB=/data/license_server.sqlite",
                f"TOKEN_TTL_DAYS={TOKEN_TTL_DAYS}",
                f"ADMIN_USER={ADMIN_USER}",
                f"ADMIN_PASS={ADMIN_PASS}",
                f"FLASK_SECRET_KEY={FLASK_SECRET_KEY}",
                f"PORT=8088",
                "",
            ]
        )
        sftp = ssh.open_sftp()
        try:
            with sftp.file(f"{REMOTE_ROOT}/.env", "w") as f:
                f.write(env_text)
        finally:
            sftp.close()

    print("[5] Start docker-compose")
    # Prefer docker-compose (CasaOS often has it)
    cmd = (
        f"cd {REMOTE_ROOT} && "
        f"(docker-compose -f docker-compose.casaos.yml --env-file .env up -d --build "
        f"|| docker compose -f docker-compose.casaos.yml --env-file .env up -d --build)"
    )
    exit_code, out_text, err_text = _run_remote(ssh, cmd, timeout_s=600)
    if exit_code == 0:
        print("    [OK] license-server started")
    else:
        print(f"    [WARN] compose exit={exit_code}")
        if err_text.strip():
            print(err_text.strip()[:500])

    print("[6] Show container")
    exit_code, out_text, err_text = _run_remote(ssh, "docker ps --format '{{.Names}}\t{{.Status}}' | grep -i license || true", timeout_s=20)
    if out_text.strip():
        print(out_text.strip())

    ssh.close()

    print("\n[SUCCESS] If running, open:")
    print(f"  http://{REMOTE_HOST}:8088/admin")


if __name__ == '__main__':
    main()
