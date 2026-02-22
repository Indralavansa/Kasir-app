from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import paramiko


def _env(name: str, default: str = "") -> str:
    return (os.environ.get(name) or default).strip()


def run(ssh: paramiko.SSHClient, cmd: str, timeout: int = 0) -> tuple[int, str, str]:
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout or None)
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    code = stdout.channel.recv_exit_status()
    return code, out, err


def main() -> int:
    host = _env("CASAOS_HOST")
    user = _env("CASAOS_USER")
    password = os.environ.get("CASAOS_PASS") or ""
    out_file = Path(_env("OUT_FILE", "d:/connect casa os/tools/_docker_root_migration.txt"))

    target_root = _env("TARGET_DOCKER_ROOT", "/DATA/docker")

    lines: list[str] = []
    lines.append(f"timestamp: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"host: {host}")
    lines.append(f"target_root: {target_root}")

    out_file.parent.mkdir(parents=True, exist_ok=True)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=20)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    steps: list[tuple[str, str]] = [
        ("df_before", "bash -lc \"df -h / /var/lib /DATA || true\""),
        ("docker_root_before", "bash -lc \"docker info --format '{{.DockerRootDir}}' || true\""),
        ("docker_system_df_before", "bash -lc \"docker system df || true\""),
        (
            "stop_docker",
            "bash -lc \"(systemctl stop docker 2>/dev/null || service docker stop 2>/dev/null || true); (systemctl stop docker.socket 2>/dev/null || true); systemctl reset-failed docker 2>/dev/null || true; echo stopped\"",
        ),
        (
            "prepare_target",
            f"bash -lc \"mkdir -p /etc/docker; if [ -d {target_root} ] && [ \"$(ls -A {target_root} 2>/dev/null)\" ]; then mv {target_root} {target_root}.pre_{ts}; fi; mkdir -p {target_root}; echo ready\"",
        ),
        (
            "copy_data",
            "bash -lc \"set -e; src=/var/lib/docker; dst="
            + target_root
            + "; "
            "if command -v rsync >/dev/null 2>&1; then "
            "  rsync -aHAX --numeric-ids $src/ $dst/ > /tmp/docker_migrate.log 2>&1; "
            "else "
            "  cp -a $src/. $dst/ > /tmp/docker_migrate.log 2>&1; "
            "fi; tail -n 60 /tmp/docker_migrate.log || true\"",
        ),
        (
            "backup_old",
            f"bash -lc \"mv /var/lib/docker /var/lib/docker.bak_{ts}; echo backed_up:{ts}\"",
        ),
        (
            "write_daemon_json",
            "bash -lc \"printf '{\\n  \\\"data-root\\\": \\\""
            + target_root
            + "\\\"\\n}\\n' > /etc/docker/daemon.json; cat /etc/docker/daemon.json\"",
        ),
        (
            "start_docker",
            "bash -lc \"systemctl reset-failed docker 2>/dev/null || true; (systemctl start docker 2>/dev/null || service docker start 2>/dev/null || true); sleep 4; docker info --format '{{.DockerRootDir}}'\"",
        ),
        ("docker_system_df_after", "bash -lc \"docker system df || true\""),
        ("df_after", "bash -lc \"df -h / /var/lib /DATA || true\""),
    ]

    for name, cmd in steps:
        code, out, err = run(ssh, cmd, timeout=900)
        lines.append("")
        lines.append(f"## {name} (exit={code})")
        if out:
            lines.append(out)
        if err:
            lines.append("ERR:")
            lines.append(err)
        # if docker fails to start, stop early
        if name == "start_docker" and (code != 0 or (out and target_root not in out)):
            lines.append("\nresult: error")
            out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
            ssh.close()
            return 1

    ssh.close()
    lines.append("")
    lines.append("result: ok")
    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
