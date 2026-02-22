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
    out_file = Path(_env("OUT_FILE", "d:/connect casa os/tools/_docker_rescue.txt"))

    lines: list[str] = []
    lines.append(f"timestamp: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"host: {host}")

    out_file.parent.mkdir(parents=True, exist_ok=True)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=20)

    cmds = [
        (
            "list_backups",
            "bash -lc \"ls -la /var/lib | grep docker || true; ls -d /var/lib/docker* 2>/dev/null || true\"",
        ),
        (
            "show_daemon_json",
            "bash -lc \"(cat /etc/docker/daemon.json 2>/dev/null || echo '(no daemon.json)')\"",
        ),
        (
            "restore_varlib",
            "bash -lc \"set -e; if [ -d /var/lib/docker ]; then echo docker_dir_ok; else if [ -d /var/lib/docker.bak_ ]; then mv /var/lib/docker.bak_ /var/lib/docker; echo restored_from:docker.bak_; else echo no_backup_found; fi; fi\"",
        ),
        (
            "write_daemon_json_recover",
            "bash -lc \"mkdir -p /etc/docker; printf '{\\n  \\\"data-root\\\": \\\"/var/lib/docker\\\"\\n}\\n' > /etc/docker/daemon.json; cat /etc/docker/daemon.json\"",
        ),
        (
            "start_docker",
            "bash -lc \"systemctl reset-failed docker 2>/dev/null || true; (systemctl start docker 2>/dev/null || service docker start 2>/dev/null || true); sleep 3; docker info --format '{{.DockerRootDir}}'\"",
        ),
        (
            "docker_service",
            "bash -lc \"(systemctl status docker --no-pager -l 2>/dev/null || true) | tail -n 60\"",
        ),
        (
            "docker_journal",
            "bash -lc \"journalctl -u docker --no-pager -n 80 2>/dev/null || true\"",
        ),
        (
            "docker_ps",
            "bash -lc \"docker ps --format '{{.Names}}|{{.Status}}|{{.Ports}}' || true\"",
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

    ssh.close()
    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
