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
    out_file = Path(_env("OUT_FILE", "d:/connect casa os/tools/_containerd_migration.txt"))

    target = _env("TARGET_CONTAINERD", "/DATA/containerd")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    lines: list[str] = []
    lines.append(f"timestamp: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"host: {host}")
    lines.append(f"target: {target}")

    out_file.parent.mkdir(parents=True, exist_ok=True)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=20)

    steps = [
        ("df_before", "bash -lc \"df -h / /var/lib /DATA || true\""),
        ("stop_services", "bash -lc \"systemctl stop docker docker.socket 2>/dev/null || true; systemctl stop containerd 2>/dev/null || true; echo stopped\""),
        (
            "prepare_target",
            f"bash -lc \"if [ -e {target} ] && [ \"$(ls -A {target} 2>/dev/null)\" ]; then mv {target} {target}.pre_{ts}; fi; mkdir -p {target}; echo ready\"",
        ),
        (
            "copy_containerd",
            f"bash -lc \"set -e; src=/var/lib/containerd; dst={target}; "
            "if [ -L $src ]; then echo 'src_is_symlink'; exit 0; fi; "
            "if command -v rsync >/dev/null 2>&1; then rsync -aHAX --numeric-ids $src/ $dst/ > /tmp/containerd_migrate.log 2>&1; else cp -a $src/. $dst/ > /tmp/containerd_migrate.log 2>&1; fi; tail -n 60 /tmp/containerd_migrate.log || true\"",
        ),
        (
            "backup_and_symlink",
            f"bash -lc \"set -e; if [ -L /var/lib/containerd ]; then echo already_symlink; else mv /var/lib/containerd /var/lib/containerd.bak_{ts}; ln -s {target} /var/lib/containerd; echo symlinked; fi\"",
        ),
        ("start_services", "bash -lc \"systemctl start containerd 2>/dev/null || true; systemctl reset-failed docker 2>/dev/null || true; systemctl start docker 2>/dev/null || true; sleep 4; docker info --format '{{.DockerRootDir}}'\""),
        ("docker_ps", "bash -lc \"docker ps --format '{{.Names}}|{{.Status}}|{{.Ports}}' || true\""),
        ("df_after", "bash -lc \"df -h / /var/lib /DATA || true\""),
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
    lines.append("")
    lines.append("result: ok")
    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
