from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from datetime import datetime
from getpass import getpass
from pathlib import Path

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


def ensure_dir(sftp: "paramiko.SFTPClient", remote_dir: str) -> None:
    parts = [p for p in remote_dir.strip("/").split("/") if p]
    cur = ""
    for part in parts:
        cur += "/" + part
        try:
            sftp.stat(cur)
        except FileNotFoundError:
            sftp.mkdir(cur)


def upload_tree(sftp: "paramiko.SFTPClient", local_root: Path, remote_root: str) -> int:
    uploaded = 0
    ensure_dir(sftp, remote_root)

    for path in local_root.rglob("*"):
        rel = path.relative_to(local_root)
        if rel.parts and rel.parts[0] in {"__pycache__", ".git"}:
            continue

        remote_path = f"{remote_root}/{rel.as_posix()}"
        if path.is_dir():
            ensure_dir(sftp, remote_path)
            continue

        ensure_dir(sftp, remote_path.rsplit("/", 1)[0])
        sftp.put(str(path), remote_path)
        uploaded += 1

    return uploaded


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

    local_root = Path(_env("LOCAL_ROOT", "d:/connect casa os/antigravity-redirect"))
    remote_root = _env("REMOTE_ROOT", "/DATA/lost+found/antigravity-redirect")
    port = int(_env("PORT", "8091"))

    if not local_root.exists():
        print(f"ERROR: local_root not found: {local_root}")
        return 1

    print(f"timestamp: {datetime.now().isoformat(timespec='seconds')}")
    print(f"host: {host}")
    print(f"user: {user}")
    print(f"local_root: {local_root.as_posix()}")
    print(f"remote_root: {remote_root}")
    print(f"port: {port}")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    _print_step("[1/4] Connecting via SSH")
    ssh.connect(host, username=user, password=password, timeout=20)

    try:
        _print_step("[2/4] Pre-flight: check port usage")
        res = run(
            ssh,
            f"bash -lc \"export TERM=dumb; docker ps --format '{{{{.Names}}}} {{{{.Ports}}}}' | grep -E ':{port}->' || true\"",
        )
        print(res.out or "(port seems free)")

        _print_step("[3/4] Upload + start service")
        sftp = ssh.open_sftp()
        try:
            count = upload_tree(sftp, local_root, remote_root)
        finally:
            sftp.close()
        print(f"uploaded_files: {count}")

        # Ensure permissions so nginx inside container can read the mounted index.html
        res = run(
            ssh,
            "bash -lc \"set -e; "
            + f"chmod 755 '{remote_root}' || true; "
            + f"chmod 644 '{remote_root}/index.html' '{remote_root}/docker-compose.yml' 2>/dev/null || true; "
            + f"ls -la '{remote_root}'\"",
        )
        if res.out:
            print(res.out)
        if res.err:
            print("ERR:\n" + res.err)

        cmd_up = (
            "bash -lc \"export TERM=dumb; "
            + f"cd '{remote_root}' && (docker compose up -d || docker-compose up -d)\""
        )
        res = run(ssh, cmd_up)
        if res.out:
            print(res.out)
        if res.err:
            print("ERR:\n" + res.err)

        _print_step("[4/4] Verify container + local curl")
        res = run(
            ssh,
            "bash -lc \"export TERM=dumb; docker ps --filter name=antigravity-redirect --format '{{.Names}}|{{.Status}}|{{.Ports}}' || true\"",
        )
        print(res.out or "(container not found)")

        res = run(
            ssh,
            "bash -lc \"docker exec antigravity-redirect ls -la /usr/share/nginx/html || true\"",
        )
        if res.out:
            print("\ncontainer /usr/share/nginx/html:\n" + res.out)

        res = run(
            ssh,
            f"bash -lc \"curl -I -s http://localhost:{port}/ | head -n 20\"",
        )
        print("\nHTTP headers (from server):\n" + (res.out or "(no response)"))
        if res.err:
            print("ERR:\n" + res.err)

        return 0

    finally:
        try:
            ssh.close()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
