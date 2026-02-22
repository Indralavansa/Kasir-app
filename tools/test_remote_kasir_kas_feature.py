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
        (
            "curl_kas",
            "bash -lc \"curl -sS -i --max-time 10 http://127.0.0.1:5000/kas | head -n 20\"",
        ),
        (
            "tables",
            "bash -lc \"docker exec kasir-toko-sembako python -c \"\"\"import sqlite3; con=sqlite3.connect('/app/instance/kasir.db'); cur=con.cursor(); cur.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'kas%';\"); print(cur.fetchall());\"\"\"\"",
        ),
        (
            "saldo",
            "bash -lc \"docker exec kasir-toko-sembako python -c 'from app_simple import KasMutasi; from app_simple import app;\nfrom app_simple import db;\nwith app.app_context():\n    print(\"saldo\", KasMutasi.saldo())'\"",
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
