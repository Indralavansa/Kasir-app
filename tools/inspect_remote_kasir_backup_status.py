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
    kasir_root = _env("KASIR_ROOT", "/DATA/lost+found/kasir-app")

    if not host:
        raise SystemExit("Missing CASAOS_HOST env var")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=20)

    print("timestamp:", datetime.now().isoformat(timespec="seconds"))
    print("kasir_root:", kasir_root)

    cmds: list[tuple[str, str]] = [
        ("ps_kasir", "bash -lc \"docker ps --filter name=kasir-toko-sembako --format '{{.Names}}|{{.Status}}|{{.Ports}}'\""),
        ("crontab_root", "bash -lc \"crontab -l 2>/dev/null || echo '(no root crontab)'\""),
        (
            "cron_d",
            "bash -lc \"ls -1 /etc/cron.d 2>/dev/null | sed -n '1,120p' || true\"",
        ),
        (
            "cron_grep_kasir",
            "bash -lc \"(grep -RIn -- 'kasir|backup|ollama|connect-ai-chat' /etc/cron.* /etc/cron.d 2>/dev/null || true) | head -n 80\"",
        ),
        (
            "host_backups_ls",
            "bash -lc \"ls -lah --time-style=long-iso "
            + kasir_root
            + "/backups 2>/dev/null | tail -n 40 || echo 'no host backups dir'\"",
        ),
        (
            "host_data_ls",
            "bash -lc \"ls -lah --time-style=long-iso "
            + kasir_root
            + "/data 2>/dev/null | tail -n 60 || echo 'no host data dir'\"",
        ),
        (
            "container_backups_ls",
            "bash -lc \"docker exec kasir-toko-sembako sh -lc 'ls -lah --time-style=long-iso /app/backups 2>/dev/null | tail -n 40 || echo no_container_backups'\"",
        ),
        (
            "container_data_ls",
            "bash -lc \"docker exec kasir-toko-sembako sh -lc 'ls -lah --time-style=long-iso /app/data 2>/dev/null | tail -n 60 || echo no_container_data'\"",
        ),
        (
            "search_backup_script",
            "bash -lc \"docker exec kasir-toko-sembako sh -lc 'ls -lah /app/tools 2>/dev/null | head -n 200 || true'\"",
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
