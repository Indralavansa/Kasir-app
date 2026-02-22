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


def ensure_dir(sftp: paramiko.SFTPClient, remote_dir: str) -> None:
    parts = [p for p in remote_dir.strip("/").split("/") if p]
    cur = ""
    for part in parts:
        cur += "/" + part
        try:
            sftp.stat(cur)
        except FileNotFoundError:
            sftp.mkdir(cur)


def main() -> int:
    host = _env("CASAOS_HOST")
    user = _env("CASAOS_USER")
    password = os.environ.get("CASAOS_PASS") or ""
    remote_root = _env("CHAT_ROOT", "/DATA/lost+found/connect-ai-chat")
    local_compose = Path(_env("LOCAL_COMPOSE", "d:/connect casa os/connect-ai-chat/docker-compose.yml"))
    local_env = Path(_env("LOCAL_ENV", "d:/connect casa os/connect-ai-chat/.env"))
    model = _env("OLLAMA_MODEL", "llama3.1:8b")
    out_file = Path(_env("OUT_FILE", "d:/connect casa os/tools/_ai_chat_update_result.txt"))

    lines = [f"timestamp: {datetime.now().isoformat(timespec='seconds')}"]

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=20)

    sftp = ssh.open_sftp()
    try:
        remote_path = f"{remote_root}/docker-compose.yml"
        ensure_dir(sftp, remote_root)
        sftp.put(str(local_compose), remote_path)
        lines.append(f"uploaded: {remote_path}")

        remote_env_path = f"{remote_root}/.env"
        if local_env.exists():
            sftp.put(str(local_env), remote_env_path)
            lines.append(f"uploaded: {remote_env_path}")
        else:
            lines.append(f"skipped (missing): {local_env}")
    finally:
        sftp.close()

    cmds = [
        (
            "restart",
            "bash -lc \"export TERM=dumb; cd "
            + remote_root
            + " && (docker compose up -d --build || docker-compose up -d --build) > /tmp/ai_chat_restart.log 2>&1; echo __EXIT:$?; tail -n 80 /tmp/ai_chat_restart.log\"",
        ),
        ("ollama_logs", "bash -lc \"docker logs --tail 120 connect-ai-chat-ollama\""),
        (
            "ollama_pull",
            "bash -lc \"export TERM=dumb; docker exec connect-ai-chat-ollama ollama pull "
            + model
            + " > /tmp/ollama_pull2.log 2>&1; echo __EXIT:$?; tail -n 80 /tmp/ollama_pull2.log\"",
        ),
        ("ps", "bash -lc \"docker ps --filter name=connect-ai-chat --format '{{.Names}}|{{.Status}}|{{.Ports}}'\""),
    ]

    for name, cmd in cmds:
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
