#!/usr/bin/env python3
"""
Check License Server Status di CasaOS
Usage: python check_license_server_casaos.py
"""

import subprocess
import sys

CASAOS_IP = "192.168.1.25"
CASAOS_USER = "root"

def run_ssh_command(cmd):
    """Run command via SSH ke CasaOS"""
    try:
        result = subprocess.run(
            ["ssh", f"{CASAOS_USER}@{CASAOS_IP}", cmd],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🔍 Checking License Server status di CasaOS...\n")
    
    # 1. Check if container exists and running
    print("1️⃣ Checking container status...")
    success, stdout, stderr = run_ssh_command(
        "docker ps --filter name=kasir-license-server --format '{{.Status}}'"
    )
    
    if success and stdout.strip():
        print(f"   ✅ Container running: {stdout.strip()}")
    else:
        print("   ❌ Container NOT running!")
        print("\n📝 Deploy license server dulu:")
        print("   cd license_server")
        print("   docker compose -f docker-compose.casaos.yml up -d --build")
        sys.exit(1)
    
    # 2. Check if server responds
    print("\n2️⃣ Checking server response...")
    success, stdout, stderr = run_ssh_command(
        f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:8088/admin"
    )
    
    if success and "200" in stdout:
        print(f"   ✅ Server responding (HTTP {stdout.strip()})")
    else:
        print(f"   ⚠️ Server not responding or not ready yet")
    
    # 3. Check database exists
    print("\n3️⃣ Checking database...")
    success, stdout, stderr = run_ssh_command(
        "docker exec kasir-license-server ls -lh /data/license_server.sqlite"
    )
    
    if success:
        print(f"   ✅ Database exists: {stdout.strip()}")
    else:
        print("   ⚠️ Database not found (will be created on first license generation)")
    
    # 4. Count existing licenses
    print("\n4️⃣ Counting existing licenses...")
    success, stdout, stderr = run_ssh_command(
        "docker exec kasir-license-server sqlite3 /data/license_server.sqlite 'SELECT COUNT(*) FROM licenses' 2>/dev/null"
    )
    
    if success and stdout.strip().isdigit():
        count = int(stdout.strip())
        print(f"   📊 Total licenses: {count}")
    else:
        print("   ℹ️ No licenses yet")
    
    print("\n" + "="*60)
    print("✅ License Server ready!")
    print("="*60)
    print("\n📝 Generate license untuk customer:")
    print("   powershell: .\\generate_customer_license.ps1 standard")
    print("   powershell: .\\generate_customer_license.ps1 trial 30")
    print("\n🌐 Admin Dashboard:")
    print(f"   http://{CASAOS_IP}:8088/admin")
    print("   Username: admin")
    print("   Password: Lavansastore")

if __name__ == "__main__":
    main()
