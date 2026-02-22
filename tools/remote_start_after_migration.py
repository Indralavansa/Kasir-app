from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

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
    user = _env("CASAOS_USER")
    password = os.environ.get("CASAOS_PASS") or ""
    out_file = Path(_env("OUT_FILE", "d:/connect casa os/tools/_after_migration_start.txt"))

    kasir_root = _env("KASIR_ROOT", "/DATA/lost+found/kasir-app")
    chat_root = _env("CHAT_ROOT", "/DATA/lost+found/connect-ai-chat")
    ollama_model = _env("OLLAMA_MODEL", "llama3.1:8b")

    lines: list[str] = []
    lines.append(f"timestamp: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"host: {host}")
    lines.append(f"kasir_root: {kasir_root}")
    lines.append(f"chat_root: {chat_root}")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=20)

    steps = [
        ("docker_root", "bash -lc \"docker info --format '{{.DockerRootDir}}'\""),
        (
            "kasir_up",
            "bash -lc \"export TERM=dumb; cd "
            + kasir_root
            + " && (docker compose up -d --build || docker-compose up -d --build) > /tmp/kasir_up.log 2>&1; echo __EXIT:$?; tail -n 60 /tmp/kasir_up.log\"",
        ),
        (
            "chat_up",
            "bash -lc \"export TERM=dumb; cd "
            + chat_root
            + " && (docker compose up -d --build || docker-compose up -d --build) > /tmp/chat_up.log 2>&1; echo __EXIT:$?; tail -n 60 /tmp/chat_up.log\"",
        ),
        (
            "ollama_pull",
            "bash -lc \"export TERM=dumb; docker exec connect-ai-chat-ollama ollama pull "
            + ollama_model
            + " > /tmp/ollama_pull.log 2>&1; echo __EXIT:$?; tail -n 40 /tmp/ollama_pull.log\"",
        ),
        (
            "ports",
            "bash -lc \"export TERM=dumb; docker ps --format '{{.Names}}|{{.Ports}}' | (grep -E ':5000->|:8090->' || true)\"",
        ),
        (
            "ps",
            "bash -lc \"export TERM=dumb; docker ps --format '{{.Names}}|{{.Status}}|{{.Ports}}' | grep -E 'kasir-toko-sembako|connect-ai-chat' || true\"",
        ),
    ]

    for name, cmd in steps:
        code, out, err = run(ssh, cmd)
        lines.append("")
        lines.append(f"## {name} (exit={code})")
        if out:
            lines.append(out)
        if err:
            lines.append("ERR:")
            lines.append(err)

    ssh.close()

    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
