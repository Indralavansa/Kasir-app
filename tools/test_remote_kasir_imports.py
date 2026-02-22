from __future__ import annotations

import os
from datetime import datetime

import paramiko


def _env(name: str, default: str = "") -> str:
    return (os.environ.get(name) or default).strip()


def run(ssh: paramiko.SSHClient, cmd: str) -> tuple[int, str, str]:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    code = stdout.channel.recv_exit_status()
    return code, out, err


def main() -> int:
    host = _env("CASAOS_HOST")
    user = _env("CASAOS_USER", "root")
    password = os.environ.get("CASAOS_PASS") or ""

    if not host:
        raise SystemExit("Missing CASAOS_HOST env var")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=20)

    print("timestamp:", datetime.now().isoformat(timespec="seconds"))

    cmds: list[tuple[str, str]] = [
        (
            "ps",
            "bash -lc \"docker ps --filter name=kasir-toko-sembako --format '{{.Names}}|{{.Status}}|{{.Ports}}'\"",
        ),
        (
            "import_app_simple",
            "bash -lc \"docker exec kasir-toko-sembako python -c 'import app_simple; print(\\\"OK app_simple imported\\\")'\"",
        ),
        (
            "import_telegram_bot",
            "bash -lc \"docker exec kasir-toko-sembako python -c 'import telegram_bot; print(\\\"OK telegram_bot imported\\\")'\"",
        ),
    ]

    for name, cmd in cmds:
        code, out, err = run(ssh, cmd)
        print("\n##", name, f"(exit={code})")
        if out:
            print(out)
        if err:
            print("ERR:")
            print(err)

    ssh.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
