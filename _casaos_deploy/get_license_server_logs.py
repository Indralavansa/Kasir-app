#!/usr/bin/env python3
import paramiko

host = '192.168.1.25'
user = 'root'
password = 'goodlife'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=20)

# Find container name containing 'license'
stdin, stdout, stderr = ssh.exec_command("docker ps -a --format '{{.Names}}' | grep -i license | head -n 1")
name = stdout.read().decode('utf-8', errors='replace').strip()

if not name:
    print('No license container found')
    ssh.close()
    raise SystemExit(1)

print('Container:', name)
stdin, stdout, stderr = ssh.exec_command(f"docker logs --tail 200 {name}")
print(stdout.read().decode('utf-8', errors='replace'))
print(stderr.read().decode('utf-8', errors='replace'))
ssh.close()
