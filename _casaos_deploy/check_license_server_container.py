#!/usr/bin/env python3
import paramiko

host = '192.168.1.25'
user = 'root'
password = 'goodlife'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=20)

cmd = "docker ps -a --format '{{.Names}}\t{{.Status}}'"
stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode('utf-8', errors='replace'))
print(stderr.read().decode('utf-8', errors='replace'))
ssh.close()
