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

    if not host:
        raise SystemExit("Missing CASAOS_HOST env var")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=20)

    print("timestamp:", datetime.now().isoformat(timespec="seconds"))

    cmds: list[tuple[str, str]] = [
        ("df", "bash -lc \"df -hT\""),
        ("mount_data", "bash -lc \"mount | egrep ' /DATA |/var/lib/docker|/var/lib/containerd|/var/lib/casaos' || true\""),
        ("docker_info", "bash -lc \"docker info 2>/dev/null | egrep 'Docker Root Dir|Storage Driver|Backing Filesystem' || true\""),
        ("ls_paths", "bash -lc \"ls -ld /DATA /var/lib/docker /var/lib/containerd /var/lib/casaos 2>/dev/null || true\""),
        (
            "du_rootfs_hotspots",
            "bash -lc \"du -sh /var/lib/docker /var/lib/containerd /var/lib/casaos 2>/dev/null || true\"",
        ),
        (
            "du_data_hotspots",
            "bash -lc \"du -sh /DATA/AppData /DATA/Packages /DATA/docker /DATA/containerd 2>/dev/null || true\"",
        ),
        (
            "casaos_paths",
            "bash -lc \"(ls -1 /var/lib/casaos 2>/dev/null || true); (find /var/lib/casaos -maxdepth 2 -type f -name '*.json' 2>/dev/null | head -n 50 || true)\"",
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
