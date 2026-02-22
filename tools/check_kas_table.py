#!/usr/bin/env python
"""Check if kas_mutasi table exists in remote DB."""

import os
import subprocess
import json

host = os.getenv("CASAOS_HOST", "192.168.1.25")
user = os.getenv("CASAOS_USER", "root")
password = os.getenv("CASAOS_PASS", "goodlife")

# SSH command to list all tables
cmd = f"sshpass -p {password} ssh -o StrictHostKeyChecking=no {user}@{host} 'docker exec kasir-toko-sembako sqlite3 /app/instance/kasir.db \".tables\"'"

try:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
    print(f"[TABLES] exit={result.returncode}")
    print(result.stdout)
    if result.stderr:
        print(f"[STDERR] {result.stderr}")
    
    # Check if kas_mutasi exists
    if "kas_mutasi" in result.stdout:
        print("\n✅ kas_mutasi table FOUND")
    else:
        print("\n❌ kas_mutasi table NOT FOUND - checking kas tables...")
        cmd2 = f"sshpass -p {password} ssh -o StrictHostKeyChecking=no {user}@{host} 'docker exec kasir-toko-sembako sqlite3 /app/instance/kasir.db \"SELECT name FROM sqlite_master WHERE type=\'table\' AND name LIKE \'kas%\';\"'"
        result2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True, timeout=10)
        print(f"[KAS QUERY] exit={result2.returncode}")
        print(result2.stdout)
        if result2.stderr:
            print(f"[STDERR] {result2.stderr}")
    
    # Check schema
    print("\n[SCHEMA CHECK]")
    cmd3 = f"sshpass -p {password} ssh -o StrictHostKeyChecking=no {user}@{host} 'docker exec kasir-toko-sembako sqlite3 /app/instance/kasir.db \".schema kas_mutasi\"'"
    result3 = subprocess.run(cmd3, shell=True, capture_output=True, text=True, timeout=10)
    print(f"exit={result3.returncode}")
    print(result3.stdout if result3.stdout else "[NO OUTPUT - TABLE MAY NOT EXIST]")
    if result3.stderr:
        print(f"[STDERR] {result3.stderr}")
    
except subprocess.TimeoutExpired:
    print(f"[ERROR] SSH command timed out")
except Exception as e:
    print(f"[ERROR] {e}")
