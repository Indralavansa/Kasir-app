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
    remote_root = _env("CASAOS_REMOTE_ROOT", "/DATA/lost+found/kasir-app")
    out_file = Path(_env("OUT_FILE", str(Path.cwd() / "tools" / "_docker_cleanup_result.txt")))

    lines: list[str] = []
    lines.append(f"timestamp: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"host: {host}")
    lines.append(f"remote_root: {remote_root}")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=20)

    steps = [
        ("docker_df_before", "bash -lc \"export TERM=dumb; docker system df || true\""),
        ("builder_prune", "bash -lc \"export TERM=dumb; docker builder prune -af || true\""),
        ("image_prune", "bash -lc \"export TERM=dumb; docker image prune -af || true\""),
        ("container_prune", "bash -lc \"export TERM=dumb; docker container prune -f || true\""),
        ("docker_df_after", "bash -lc \"export TERM=dumb; docker system df || true\""),
        (
            "compose_build_up",
            "bash -lc \"export TERM=dumb; cd "
            + remote_root
            + " && (docker compose up -d --build || docker-compose up -d --build) > /tmp/kasir_compose_up.log 2>&1; echo __EXIT:$?; tail -n 120 /tmp/kasir_compose_up.log\"",
        ),
        ("ps", "bash -lc \"export TERM=dumb; docker ps --filter name=kasir-toko-sembako --format '{{.Names}}|{{.Status}}|{{.Ports}}' || true\""),
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

    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
