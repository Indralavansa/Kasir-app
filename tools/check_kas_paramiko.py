#!/usr/bin/env python
"""Check kas_mutasi table in remote DB using paramiko."""

import os
import sys

try:
    import paramiko
except ImportError:
    print("Installing paramiko...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "paramiko"], check=False)
    import paramiko

host = os.getenv("CASAOS_HOST", "192.168.1.25")
user = os.getenv("CASAOS_USER", "root")
password = os.getenv("CASAOS_PASS", "goodlife")

try:
    # SSH connection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    # Check tables
    print("[Step 1] Checking all tables...")
    stdin, stdout, stderr = ssh.exec_command("docker exec kasir-toko-sembako sqlite3 /app/instance/kasir.db '.tables'")
    tables = stdout.read().decode('utf-8', errors='ignore').strip()
    err = stderr.read().decode('utf-8', errors='ignore').strip()
    
    print(f"Tables: {tables}")
    if err:
        print(f"Error: {err}")
    
    if "kas_mutasi" in tables:
        print("✅ kas_mutasi table FOUND")
        
        # Get row count
        print("\n[Step 2] Checking kas_mutasi schema & row count...")
        stdin, stdout, stderr = ssh.exec_command("docker exec kasir-toko-sembako sqlite3 /app/instance/kasir.db \"SELECT COUNT(*) FROM kas_mutasi; .schema kas_mutasi;\"")
        info = stdout.read().decode('utf-8', errors='ignore').strip()
        print(info)
        
        # Get sample data
        print("\n[Step 3] Sample data (last 3 records)...")
        stdin, stdout, stderr = ssh.exec_command("docker exec kasir-toko-sembako sqlite3 /app/instance/kasir.db \"SELECT id, tipe, jumlah, keterangan, date(tanggal) FROM kas_mutasi ORDER BY tanggal DESC LIMIT 3;\"")
        data = stdout.read().decode('utf-8', errors='ignore').strip()
        print(data)
        
    else:
        print("❌ kas_mutasi table NOT FOUND")
        print(f"Available tables: {tables}")
        
        # Try creating it
        print("\n[Attempting] Let's trigger table creation via Flask app...")
        stdin, stdout, stderr = ssh.exec_command("docker exec kasir-toko-sembako curl -s http://localhost:5000/ | head -20")
        resp = stdout.read().decode('utf-8', errors='ignore')
        print(f"Flask response: {resp[:200]}")
        
        # Check tables again
        print("\n[Re-checking] tables after Flask request...")
        stdin, stdout, stderr = ssh.exec_command("docker exec kasir-toko-sembako sqlite3 /app/instance/kasir.db '.tables'")
        tables = stdout.read().decode('utf-8', errors='ignore').strip()
        print(f"Tables now: {tables}")
        if "kas_mutasi" in tables:
            print("✅ kas_mutasi created after Flask init")
        else:
            print("❌ kas_mutasi still missing")
    
    ssh.close()
    
except Exception as e:
    import traceback
    print(f"ERROR: {e}")
    traceback.print_exc()
