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


def upload_tree(sftp: paramiko.SFTPClient, local_root: Path, remote_root: str) -> int:
    uploaded = 0
    ensure_dir(sftp, remote_root)

    for path in local_root.rglob("*"):
        rel = path.relative_to(local_root)
        if rel.parts and rel.parts[0] in {"__pycache__", ".git"}:
            continue

        remote_path = f"{remote_root}/{rel.as_posix()}"
        if path.is_dir():
            ensure_dir(sftp, remote_path)
            continue

        ensure_dir(sftp, remote_path.rsplit("/", 1)[0])
        sftp.put(str(path), remote_path)
        uploaded += 1

    return uploaded


def main() -> int:
    host = _env("CASAOS_HOST")
    user = _env("CASAOS_USER")
    password = os.environ.get("CASAOS_PASS") or ""

    local_root = Path(_env("LOCAL_ROOT", "d:/connect casa os/connect-ai-chat"))
    remote_root = _env("CASAOS_REMOTE_ROOT", "/DATA/lost+found/connect-ai-chat")
    out_file = Path(_env("OUT_FILE", "d:/connect casa os/tools/_deploy_connect_ai_chat_result.txt"))

    lines: list[str] = []
    lines.append(f"timestamp: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"host: {host}")
    lines.append(f"remote_root: {remote_root}")
    lines.append(f"local_root: {local_root.as_posix()}")

    out_file.parent.mkdir(parents=True, exist_ok=True)

    if not host or not user or not password:
        lines.append("result: error")
        lines.append("missing env: CASAOS_HOST, CASAOS_USER, CASAOS_PASS")
        out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return 1

    if not local_root.exists():
        lines.append("result: error")
        lines.append(f"LOCAL_ROOT not found: {local_root}")
        out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return 1

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(host, username=user, password=password, timeout=20)

        # Pre-flight: check port 8090 usage
        code, out, err = run(
            ssh,
            "bash -lc \"export TERM=dumb; docker ps --format '{{.Names}} {{.Ports}}' | grep -E ':8090->' || true\"",
        )
        lines.append("")
        lines.append(f"## port_8090_check (exit={code})")
        if out:
            lines.append(out)
        if err:
            lines.append("ERR:")
            lines.append(err)

        sftp = ssh.open_sftp()
        try:
            count = upload_tree(sftp, local_root, remote_root)
            lines.append("")
            lines.append(f"uploaded_files: {count}")
        finally:
            sftp.close()

        # Deploy
        deploy_log = "/tmp/connect_ai_chat_deploy.log"
        cmd_up = (
            "bash -lc \"export TERM=dumb; "
            + f"cd {remote_root} && (docker compose up -d --build || docker-compose up -d --build) > {deploy_log} 2>&1; "
            + "echo __EXIT:$?; tail -n 120 "
            + deploy_log
            + "\""
        )
        code, out, err = run(ssh, cmd_up)
        lines.append("")
        lines.append(f"## compose_up (exit={code})")
        if out:
            lines.append(out)
        if err:
            lines.append("ERR:")
            lines.append(err)

        # Pull model
        model = _env("OLLAMA_MODEL", "llama3.1:8b")
        pull_log = "/tmp/ollama_pull.log"
        cmd_pull = (
            "bash -lc \"export TERM=dumb; "
            + f"docker exec connect-ai-chat-ollama ollama pull {model} > {pull_log} 2>&1; "
            + "echo __EXIT:$?; tail -n 80 "
            + pull_log
            + "\""
        )
        code, out, err = run(ssh, cmd_pull)
        lines.append("")
        lines.append(f"## ollama_pull (exit={code})")
        if out:
            lines.append(out)
        if err:
            lines.append("ERR:")
            lines.append(err)

        # Status
        code, out, err = run(
            ssh,
            "bash -lc \"export TERM=dumb; docker ps --filter name=connect-ai-chat --format '{{.Names}}|{{.Status}}|{{.Ports}}' || true\"",
        )
        lines.append("")
        lines.append(f"## ps (exit={code})")
        if out:
            lines.append(out)
        if err:
            lines.append("ERR:")
            lines.append(err)

        lines.append("")
        lines.append("result: ok")
        out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return 0

    except Exception as e:
        lines.append("")
        lines.append("result: error")
        lines.append(repr(e))
        out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return 1
    finally:
        try:
            ssh.close()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
