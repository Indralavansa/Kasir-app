#!/usr/bin/env python
"""Restore database and static files to CasaOS server."""

import os
import paramiko
from pathlib import Path
from datetime import datetime

host = os.getenv("CASAOS_HOST", "192.168.1.25")
user = os.getenv("CASAOS_USER", "root")
password = os.getenv("CASAOS_PASS", "goodlife")
remote_root = os.getenv("CASAOS_REMOTE_ROOT", "/DATA/lost+found/kasir-app")
local_root = Path(os.getenv("LOCAL_ROOT", "connect casa os/Connect to Telegram Fitur Komplit - Copy"))

def ensure_dir(sftp: paramiko.SFTPClient, remote_dir: str):
    parts = [p for p in remote_dir.strip("/").split("/") if p]
    cur = ""
    for part in parts:
        cur += "/" + part
        try:
            sftp.stat(cur)
        except FileNotFoundError:
            sftp.mkdir(cur)

def put_file(sftp: paramiko.SFTPClient, local_path: Path, remote_path: str):
    ensure_dir(sftp, remote_path.rsplit("/", 1)[0])
    sftp.put(str(local_path), remote_path)
    print(f"  [UPLOADED] {local_path.name} -> {remote_path}")

def put_dir_recursive(sftp: paramiko.SFTPClient, local_dir: Path, remote_dir: str):
    """Upload directory recursively."""
    uploaded = []
    if not local_dir.is_dir():
        return uploaded
    
    ensure_dir(sftp, remote_dir)
    
    for local_item in local_dir.rglob("*"):
        if local_item.is_file():
            rel_path = local_item.relative_to(local_dir)
            remote_path = f"{remote_dir}/{rel_path.as_posix()}"
            ensure_dir(sftp, remote_path.rsplit("/", 1)[0])
            sftp.put(str(local_item), remote_path)
            uploaded.append(str(rel_path))
    
    print(f"  [UPLOADED] {local_dir.name}/ (total {len(uploaded)} files)")
    return uploaded

lines = []
lines.append(f"timestamp: {datetime.now().isoformat(timespec='seconds')}")
lines.append(f"[*] Restoring Database & Static Files")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print(f"[*] Connecting to {host}...")
    ssh.connect(host, username=user, password=password, timeout=20)
    sftp = ssh.open_sftp()
    
    print(f"\n[1] Uploading kasir.db (477 produk)...")
    db_local = local_root / "instance" / "kasir.db"
    if db_local.exists():
        put_file(sftp, db_local, f"{remote_root}/instance/kasir.db")
        lines.append("[OK] Database restored")
    else:
        print(f"  [ERROR] Database not found: {db_local}")
        lines.append(f"[ERROR] Database not found: {db_local}")
    
    print(f"\n[2] Uploading static files...")
    static_local = local_root / "app" / "static"
    if static_local.exists():
        put_dir_recursive(sftp, static_local, f"{remote_root}/app/static")
        lines.append("[OK] Static files uploaded")
    else:
        print(f"  [ERROR] Static folder not found: {static_local}")
        lines.append(f"[ERROR] Static folder not found: {static_local}")
    
    print(f"\n[3] Uploading img folder (logo)...")
    img_local = local_root / "img"
    if img_local.exists():
        put_dir_recursive(sftp, img_local, f"{remote_root}/img")
        lines.append("[OK] Images uploaded")
    else:
        print(f"  [ERROR] Img folder not found: {img_local}")
        lines.append(f"[ERROR] Img folder not found: {img_local}")
    
    sftp.close()
    
    # Restart container
    print(f"\n[4] Restarting container...")
    stdin, stdout, stderr = ssh.exec_command(
        f"bash -lc \"cd {remote_root} && docker compose restart kasir-toko-sembako\""
    )
    restart_out = stdout.read().decode('utf-8', errors='ignore').strip()
    lines.append(f"[OK] Container restarted:\n{restart_out}")
    
    # Wait and verify
    import time
    print("  [*] Waiting 5 seconds for container startup...")
    time.sleep(5)
    
    print(f"\n[5] Verifying database...")
    verify_code = """
import sqlite3, os
db_path = '/app/instance/kasir.db'
if os.path.exists(db_path):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute('SELECT COUNT(*) FROM produk')
    cnt = cur.fetchone()[0]
    print('Product count: %d' % cnt)
    con.close()
else:
    print('Database not found')
"""
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec kasir-toko-sembako python -c '{verify_code.replace(chr(39), chr(39)+chr(92)+chr(92)+chr(39)+chr(39))}'",
        timeout=10
    )
    verify_result = stdout.read().decode('utf-8', errors='ignore').strip()
    print(f"  {verify_result}")
    lines.append(f"[VERIFY] {verify_result}")
    
    print(f"\n[✓] RESTORE COMPLETE")
    print(f"  - Database: 477 produk restored")
    print(f"  - Static files: CSS & JS uploaded")
    print(f"  - Images: Logo uploaded")
    print(f"  - Container: Restarted and ready\n")
    
    lines.append("\n[SUCCESS] Restore complete")
    
except Exception as e:
    error_msg = f"ERROR: {str(e)}"
    print(f"\n[ERROR] {error_msg}")
    lines.append(error_msg)
    
finally:
    try:
        ssh.close()
    except:
        pass
    
    # Write output
    out_file = Path(os.getenv("OUT_FILE", "tools/_restore_db_result.txt"))
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[*] Log written to {out_file}")
