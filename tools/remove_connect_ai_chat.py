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

    remote_root = _env("CHAT_ROOT", "/DATA/lost+found/connect-ai-chat")

    print(f"timestamp: {datetime.now().isoformat(timespec='seconds')}")
    print(f"host: {host}")
    print(f"user: {user}")
    print(f"remote_root: {remote_root}")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    _print_step("[1/6] Connecting via SSH")
    ssh.connect(host, username=user, password=password, timeout=20)

    try:
        _print_step("[2/6] Current status (docker ps)")
        res = run(
            ssh,
            "bash -lc \"export TERM=dumb; docker ps -a --filter name=connect-ai-chat --format '{{.Names}}|{{.Status}}|{{.Image}}|{{.Ports}}' || true\"",
        )
        print(res.out or "(no matching containers)")
        if res.err:
            print("ERR:\n" + res.err)

        _print_step("[3/6] Stopping + removing via compose (preferred)")
        cmd_down = (
            "bash -lc \"export TERM=dumb; "
            + f"if [ -d '{remote_root}' ]; then cd '{remote_root}'; "
            + "(docker compose down --rmi all -v --remove-orphans || docker-compose down --rmi all -v --remove-orphans) || true; "
            + "else echo 'remote_root not found, skipping compose down'; fi\""
        )
        res = run(ssh, cmd_down)
        print(res.out)
        if res.err:
            print("ERR:\n" + res.err)

        _print_step("[4/6] Force remove leftover containers/images/volumes")
        cmds = [
            # containers
            "bash -lc \"docker rm -f connect-ai-chat connect-ai-chat-ollama 2>/dev/null || true\"",
            # images
            "bash -lc \"docker image rm -f connect-ai-chat:latest 2>/dev/null || true\"",
            "bash -lc \"docker image rm -f ollama/ollama:latest 2>/dev/null || true\"",
            # volumes / networks created by compose
            "bash -lc \"docker volume rm -f connect-ai-chat_ollama 2>/dev/null || true\"",
            "bash -lc \"docker network rm connect-ai-chat_default 2>/dev/null || true\"",
        ]
        for c in cmds:
            res = run(ssh, c)
            if res.out:
                print(res.out)
            if res.err:
                # ignore noisy errors if already removed
                pass

        _print_step("[5/6] Remove remote folder (deployment files)")
        res = run(
            ssh,
            "bash -lc \"if [ -d '" + remote_root + "' ]; then rm -rf '" + remote_root + "'; echo 'removed: "
            + remote_root
            + "'; else echo 'folder not found'; fi\"",
        )
        print(res.out)
        if res.err:
            print("ERR:\n" + res.err)

        _print_step("[6/6] Verify removed")
        res = run(
            ssh,
            "bash -lc \"export TERM=dumb; docker ps -a --filter name=connect-ai-chat --format '{{.Names}}|{{.Status}}|{{.Image}}' || true\"",
        )
        print(res.out or "✅ no matching containers")
        if res.err:
            print("ERR:\n" + res.err)

        print("\nDONE")
        return 0

    finally:
        try:
            ssh.close()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
