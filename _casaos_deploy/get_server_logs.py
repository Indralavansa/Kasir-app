#!/usr/bin/env python3
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.25', username='root', password='goodlife', timeout=15)

# Get detailed logs
stdin, stdout, stderr = ssh.exec_command('docker logs kasir-toko-sembako 2>&1 | tail -300', timeout=20)
logs = stdout.read().decode('utf-8', errors='replace')

print(logs)

ssh.close()
