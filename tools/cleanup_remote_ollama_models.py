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
    keep = _env("KEEP_MODEL", "qwen2.5:0.5b")
    remove = [m.strip() for m in _env("REMOVE_MODELS", "llama3.1:8b,llama3.2:1b").split(",") if m.strip()]

    if not host:
        raise SystemExit("Missing CASAOS_HOST env var")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=20)

    print("timestamp:", datetime.now().isoformat(timespec="seconds"))
    print("keep:", keep)
    print("remove:", remove)

    cmds: list[tuple[str, str]] = [
        ("before_list", "bash -lc \"docker exec connect-ai-chat-ollama ollama list\""),
    ]

    if remove:
        # Ollama rm is idempotent-ish; if model missing it will error, so we tolerate failures.
        rm_args = " ".join(remove)
        cmds.append(("rm_models", f"bash -lc \"docker exec connect-ai-chat-ollama ollama rm {rm_args} || true\""))

    # Prune unused layers/blobs if supported.
    cmds.append(("prune", "bash -lc \"docker exec connect-ai-chat-ollama ollama prune || true\""))
    cmds.append(("after_list", "bash -lc \"docker exec connect-ai-chat-ollama ollama list\""))
    cmds.append(("df", "bash -lc \"df -h /DATA /media/devmon/sda1-ata-HGST_HTS541075A9 2>/dev/null || df -h\""))

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
