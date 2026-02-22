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
    out_file = Path(_env("OUT_FILE", "d:/connect casa os/tools/_casaos_disk_status.txt"))

    lines: list[str] = []
    lines.append(f"timestamp: {datetime.now().isoformat(timespec='seconds')}")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=20)

    cmds = [
        ("df_root", "bash -lc \"df -h / /var/lib /DATA 2>/dev/null || df -h\""),
        ("docker_root", "bash -lc \"docker info --format '{{.DockerRootDir}}'\""),
        ("docker_system_df", "bash -lc \"docker system df\""),
        ("images", "bash -lc \"docker images --format '{{.Repository}}:{{.Tag}} {{.Size}}' | head -n 50\""),
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
