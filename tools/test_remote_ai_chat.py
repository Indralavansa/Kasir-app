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

    checks: list[tuple[str, str]] = [
        (
            "ps",
            "bash -lc \"docker ps --filter name=connect-ai-chat --format '{{.Names}}|{{.Status}}|{{.Ports}}'\"",
        ),
        ("ollama_list", "bash -lc \"docker exec connect-ai-chat-ollama ollama list\""),
        (
            "ollama_generate_from_app",
            "bash -lc 'docker exec connect-ai-chat python -c "
            "\"import os,requests; "
            "base=(os.environ.get(\\\"OLLAMA_BASE_URL\\\",\\\"http://ollama:11434\\\") or \\\"http://ollama:11434\\\").rstrip(\\\"/\\\"); "
            "model=(os.environ.get(\\\"OLLAMA_MODEL\\\",\\\"llama3.1:8b\\\") or \\\"llama3.1:8b\\\").strip(); "
            "r=requests.post(base+\\\"/api/generate\\\", json={\\\"model\\\":model,\\\"prompt\\\":\\\"say hello in Indonesian, max 5 words\\\",\\\"stream\\\":False}, timeout=120); "
            "print(\\\"status\\\", r.status_code); "
            "print(r.text[:500])" 
            "\"'",
        ),
    ]

    print("timestamp:", datetime.now().isoformat(timespec="seconds"))
    for name, cmd in checks:
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
