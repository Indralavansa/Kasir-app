#!/usr/bin/env python3
import paramiko
import time

host = '192.168.1.25'
user = 'root'
password = 'goodlife'
root = '/DATA/AppData/kasir-license-server'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=30)

cmd = (
    f"cd {root} && "
    f"(docker-compose -f docker-compose.casaos.yml --env-file .env up -d --build "
    f"|| docker compose -f docker-compose.casaos.yml --env-file .env up -d --build)"
)
stdin, stdout, stderr = ssh.exec_command(cmd)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print(out.strip())
print(err.strip())

# Give it a moment
time.sleep(2)
stdin, stdout, stderr = ssh.exec_command("docker ps -a --format '{{.Names}}\t{{.Status}}' | grep -i license || true")
print(stdout.read().decode('utf-8', errors='replace').strip())
ssh.close()
