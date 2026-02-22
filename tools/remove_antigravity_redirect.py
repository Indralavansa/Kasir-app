from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from datetime import datetime
from getpass import getpass

try:
    import paramiko  # type: ignore
except ImportError:
    print("Installing paramiko...")
    import subprocess

    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "paramiko"], check=False)
    import paramiko  # type: ignore


@dataclass(frozen=True)
class RunResult:
    code: int
    out: str
    err: str


def _env(name: str, default: str = "") -> str:
    return (os.environ.get(name) or default).strip()


def run(ssh: "paramiko.SSHClient", cmd: str) -> RunResult:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    code = stdout.channel.recv_exit_status()
    return RunResult(code=code, out=out, err=err)


def _print_step(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def main() -> int:
    host = _env("CASAOS_HOST", "192.168.1.25")
    user = _env("CASAOS_USER", "root")
    password = os.environ.get("CASAOS_PASS") or ""
    if not password:
        password = getpass(f"SSH password for {user}@{host}: ")

    remote_root = _env("REMOTE_ROOT", "/DATA/lost+found/antigravity-redirect")

    print(f"timestamp: {datetime.now().isoformat(timespec='seconds')}")
    print(f"host: {host}")
    print(f"user: {user}")
    print(f"remote_root: {remote_root}")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    _print_step("[1/4] Connecting via SSH")
    ssh.connect(host, username=user, password=password, timeout=20)

    try:
        _print_step("[2/4] Stop + remove via compose (if folder exists)")
        cmd_down = (
            "bash -lc \"export TERM=dumb; "
            + f"if [ -d '{remote_root}' ]; then cd '{remote_root}'; "
            + "(docker compose down --rmi local -v --remove-orphans || docker-compose down --rmi local -v --remove-orphans) || true; "
            + "else echo 'remote_root not found, skipping compose down'; fi\""
        )
        res = run(ssh, cmd_down)
        if res.out:
            print(res.out)
        if res.err:
            print("ERR:\n" + res.err)

        _print_step("[3/4] Force remove leftover container/network")
        cmds = [
            "bash -lc \"docker rm -f antigravity-redirect 2>/dev/null || true\"",
            "bash -lc \"docker network rm antigravity-redirect_default 2>/dev/null || true\"",
        ]
        for c in cmds:
            run(ssh, c)

        _print_step("[4/4] Remove remote folder + verify")
        res = run(
            ssh,
            "bash -lc \"if [ -d '" + remote_root + "' ]; then rm -rf '" + remote_root + "'; echo 'removed: "
            + remote_root
            + "'; else echo 'folder not found'; fi\"",
        )
        print(res.out)

        res = run(
            ssh,
            "bash -lc \"export TERM=dumb; docker ps -a --filter name=antigravity-redirect --format '{{.Names}}|{{.Status}}|{{.Ports}}' || true\"",
        )
        print(res.out or "✅ no matching containers")

        return 0

    finally:
        try:
            ssh.close()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
