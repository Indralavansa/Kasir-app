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
    out_file = Path(_env("OUT_FILE", "d:/connect casa os/tools/_docker_ext4_switch.txt"))

    mount = _env("HDD_MOUNT", "/media/devmon/sda1-ata-HGST_HTS541075A9")
    docker_root = f"{mount}/docker"
    containerd_root = f"{mount}/containerd"

    lines: list[str] = []
    lines.append(f"timestamp: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"mount: {mount}")
    lines.append(f"docker_root: {docker_root}")
    lines.append(f"containerd_root: {containerd_root}")

    out_file.parent.mkdir(parents=True, exist_ok=True)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=20)

    steps = [
        ("df", f"bash -lc \"df -Th /DATA {mount} || true\""),
        (
            "stop_services",
            "bash -lc \"systemctl stop docker docker.socket 2>/dev/null || true; systemctl stop containerd 2>/dev/null || true; systemctl reset-failed docker 2>/dev/null || true; echo stopped\"",
        ),
        (
            "prepare_dirs",
            f"bash -lc \"mkdir -p {docker_root} {containerd_root} /etc/docker; echo ready\"",
        ),
        (
            "fix_containerd_link",
            f"bash -lc \"rm -rf /var/lib/containerd; ln -s {containerd_root} /var/lib/containerd; ls -l /var/lib/containerd\"",
        ),
        (
            "write_daemon_json",
            "bash -lc \"printf '{\\n  \\\"data-root\\\": \\\""
            + docker_root
            + "\\\"\\n}\\n' > /etc/docker/daemon.json; cat /etc/docker/daemon.json\"",
        ),
        (
            "start_services",
            "bash -lc \"systemctl start containerd 2>/dev/null || true; systemctl start docker 2>/dev/null || true; sleep 4; docker info --format '{{.DockerRootDir}}'\"",
        ),
        ("docker_system_df", "bash -lc \"docker system df || true\""),
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
