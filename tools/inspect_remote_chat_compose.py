from __future__ import annotations

import os
from pathlib import Path

import paramiko


def _env(name: str, default: str = "") -> str:
    return (os.environ.get(name) or default).strip()


def main() -> int:
    host = _env("CASAOS_HOST")
    user = _env("CASAOS_USER", "root")
    password = os.environ.get("CASAOS_PASS") or ""
    remote_root = _env("CHAT_ROOT", "/DATA/lost+found/connect-ai-chat")
    remote_compose = f"{remote_root}/docker-compose.yml"

    if not host:
        raise SystemExit("Missing CASAOS_HOST env var")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=20)

    stdin, stdout, stderr = ssh.exec_command(f"bash -lc 'sed -n \"1,260p\" {remote_compose}'")
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    code = stdout.channel.recv_exit_status()
    ssh.close()

    print(f"REMOTE_COMPOSE: {remote_compose} (exit={code})")
    if err.strip():
        print("REMOTE_ERR:")
        print(err.strip())

    keys = [
        "services:",
        "ollama:",
        "image:",
        "entrypoint:",
        "command:",
        "environment:",
        "OLLAMA_HOST",
        "ports:",
        "volumes:",
        "healthcheck:",
    ]

    for i, line in enumerate(out.splitlines(), 1):
        if any(k in line for k in keys):
            print(f"{i:>4}: {line}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
