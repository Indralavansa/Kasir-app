from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import paramiko

HOST = os.environ.get("CASAOS_HOST", "").strip()
USER = os.environ.get("CASAOS_USER", "").strip()
PASS = os.environ.get("CASAOS_PASS", "")
OUT = Path(os.environ.get("OUT_FILE", "d:/connect casa os/tools/_casaos_fs_type.txt"))

MOUNT = "/media/devmon/sda1-ata-HGST_HTS541075A9"


def run(ssh: paramiko.SSHClient, cmd: str):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    code = stdout.channel.recv_exit_status()
    return code, out.strip(), err.strip()


def main() -> int:
    lines = [f"timestamp: {datetime.now().isoformat(timespec='seconds')}"]

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS, timeout=20)

    cmds = [
        ("df", f"bash -lc \"df -Th /DATA {MOUNT} 2>/dev/null || true\""),
        ("stat_data", "bash -lc \"stat -f -c '%T %m' /DATA\""),
        ("stat_mount", f"bash -lc \"stat -f -c '%T %m' {MOUNT}\""),
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
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
