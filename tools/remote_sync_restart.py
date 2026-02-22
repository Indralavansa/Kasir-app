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


def put_file(sftp: paramiko.SFTPClient, local_path: Path, remote_path: str) -> None:
    ensure_dir(sftp, remote_path.rsplit("/", 1)[0])
    sftp.put(str(local_path), remote_path)


def put_dir_recursive(sftp: paramiko.SFTPClient, local_dir: Path, remote_dir: str) -> list[str]:
    """Recursively upload directory and return list of uploaded files."""
    uploaded = []
    if not local_dir.is_dir():
        return uploaded
    
    ensure_dir(sftp, remote_dir)
    
    for local_item in local_dir.rglob("*"):
        if local_item.is_file():
            rel_path = local_item.relative_to(local_dir)
            remote_path = f"{remote_dir}/{rel_path.as_posix()}"
            ensure_dir(sftp, remote_path.rsplit("/", 1)[0])
            sftp.put(str(local_item), remote_path)
            uploaded.append(str(rel_path))
    
    return uploaded


def main() -> int:
    host = _env("CASAOS_HOST")
    user = _env("CASAOS_USER")
    password = os.environ.get("CASAOS_PASS") or ""
    remote_root = _env("CASAOS_REMOTE_ROOT", "/DATA/lost+found/kasir-app")

    if not host or not user or not password:
        raise SystemExit("Missing env: CASAOS_HOST, CASAOS_USER, CASAOS_PASS")

    local_root = Path(_env("LOCAL_ROOT"))
    if not local_root.exists():
        raise SystemExit(f"LOCAL_ROOT not found: {local_root}")

    out_file = Path(_env("OUT_FILE", str(Path.cwd() / "tools" / "_telegram_fix_result.txt")))

    lines: list[str] = []
    lines.append(f"timestamp: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"host: {host}")
    lines.append(f"remote_root: {remote_root}")
    lines.append(f"local_root: {local_root.as_posix()}")

    out_file.parent.mkdir(parents=True, exist_ok=True)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(host, username=user, password=password, timeout=20)

        sftp = ssh.open_sftp()
        try:
            # Sync individual files
            file_sync = [
                (local_root / "Dockerfile", f"{remote_root}/Dockerfile"),
                (local_root / "app" / "app_simple.py", f"{remote_root}/app/app_simple.py"),
                (local_root / "app" / "telegram_bot.py", f"{remote_root}/app/telegram_bot.py"),
                (local_root / "requirements.txt", f"{remote_root}/requirements.txt"),
                (local_root / "docker-compose.yml", f"{remote_root}/docker-compose.yml"),
                (local_root / ".env", f"{remote_root}/.env"),
                (local_root / "telegram_bot.py", f"{remote_root}/telegram_bot.py"),
                (local_root / "app_simple.py", f"{remote_root}/app_simple.py"),
            ]
            
            for lp, rp in file_sync:
                if not lp.exists():
                    lines.append(f"MISSING_LOCAL: {lp}")
                    continue
                put_file(sftp, lp, rp)
                lines.append(f"SYNC_OK: {lp.name} -> {rp}")
            
            # Sync entire templates directory recursively
            templates_local = local_root / "app" / "templates"
            templates_remote = f"{remote_root}/app/templates"
            if templates_local.exists():
                uploaded = put_dir_recursive(sftp, templates_local, templates_remote)
                lines.append(f"SYNC_OK: templates/ -> {templates_remote} ({len(uploaded)} files)")
                for f in uploaded[:5]:  # Show first 5 files
                    lines.append(f"  - {f}")
                if len(uploaded) > 5:
                    lines.append(f"  ... and {len(uploaded) - 5} more files")
            else:
                lines.append(f"MISSING_LOCAL: {templates_local}")
        finally:
            sftp.close()

        remote_log = "/tmp/kasir_compose_up.log"
        cmds = [
            (
                "compose_down",
                f"bash -lc \"export TERM=dumb; cd {remote_root} && (docker compose down || docker-compose down)\"",
            ),
            (
                "compose_up",
                "bash -lc \"export TERM=dumb; "
                + f"cd {remote_root} && (docker compose up -d --build || docker-compose up -d --build) > {remote_log} 2>&1; "
                + "echo __EXIT:$?; tail -n 80 "
                + remote_log
                + "\"",
            ),
            (
                "env_check",
                "bash -lc \"export TERM=dumb; docker exec kasir-toko-sembako python -c 'import os; t=os.getenv(\\\"TELEGRAM_BOT_TOKEN\\\",\\\"\\\"); a=os.getenv(\\\"TELEGRAM_ADMIN_CHAT_IDS\\\",\\\"\\\"); print(\\\"TOKEN_LEN=\\\", len(t)); print(\\\"ADMIN_SET=\\\", bool(a.strip()))'\"",
            ),
            (
                "ps",
                "bash -lc \"export TERM=dumb; docker ps --filter name=kasir-toko-sembako --format '{{.Names}}|{{.Status}}|{{.Ports}}'\"",
            ),
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

        lines.append("\nresult: ok")
        out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return 0

    except Exception as e:
        lines.append("\nresult: error")
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
