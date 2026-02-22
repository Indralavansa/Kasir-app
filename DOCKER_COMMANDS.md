# 🐳 Docker Quick Reference - Kasir Toko Sembako

Panduan cepat command Docker yang sering digunakan untuk manage aplikasi.

## 🚀 Setup & Start

```bash
# Setup awal (first time only)
bash setup-docker.sh        # Linux/Mac
# atau
.\setup-docker.ps1          # Windows PowerShell

# Start aplikasi
docker-compose up -d

# Start with rebuild
docker-compose up -d --build
```

## 🛑 Stop & Restart

```bash
# Stop aplikasi
docker-compose stop

# Stop dan remove container
docker-compose down

# Restart aplikasi
docker-compose restart

# Restart specific service
docker-compose restart kasir-app
```

## 📊 Monitoring & Logs

```bash
# Check status
docker-compose ps

# View logs (all)
docker-compose logs

# View logs (follow/tail)
docker-compose logs -f

# View logs (last 50 lines)
docker-compose logs --tail=50

# View logs (specific service)
docker-compose logs kasir-app

# Check resource usage
docker stats kasir-toko-sembako
```

## 🔧 Maintenance

```bash
# Masuk ke container (bash)
docker exec -it kasir-toko-sembako bash

# Masuk ke container (sh)
docker exec -it kasir-toko-sembako sh

# Run command in container
docker exec kasir-toko-sembako python --version

# Copy file from container
docker cp kasir-toko-sembako:/app/instance/kasir.db ./backup-db.db

# Copy file to container
docker cp ./new-config.py kasir-toko-sembako:/app/config.py
```

## 🔄 Update & Rebuild

```bash
# Pull latest code (if using git)
git pull

# Rebuild image
docker-compose build

# Rebuild with no cache
docker-compose build --no-cache

# Update and restart
docker-compose down
docker-compose up -d --build
```

## 💾 Backup & Restore

```bash
# Backup database (manual)
docker exec kasir-toko-sembako python tools/backup_otomatis_standalone.py

# Backup semua data
docker exec kasir-toko-sembako tar -czf /app/backups/full-backup.tar.gz /app/instance /app/data

# Copy backup ke host
docker cp kasir-toko-sembako:/app/backups/full-backup.tar.gz ./

# Restore ke container
docker cp ./full-backup.tar.gz kasir-toko-sembako:/app/backups/
```

## 🗑️ Cleanup

```bash
# Remove stopped containers
docker-compose down

# Remove containers and volumes
docker-compose down -v

# Remove images
docker rmi kasir-toko-sembako

# Clean unused resources
docker system prune

# Clean everything (CAREFUL!)
docker system prune -a --volumes
```

## 🐛 Troubleshooting

```bash
# Check container health
docker inspect kasir-toko-sembako | grep -A 10 Health

# View environment variables
docker exec kasir-toko-sembako env

# Check disk usage
docker system df

# Check network
docker network ls
docker network inspect [network-name]

# Force recreate container
docker-compose up -d --force-recreate

# Check port binding
docker port kasir-toko-sembako
```

## 🔍 Debugging

```bash
# Interactive python shell in container
docker exec -it kasir-toko-sembako python

# Check database
docker exec -it kasir-toko-sembako bash
cd instance
sqlite3 kasir.db
# SQLite commands:
# .tables          - list tables
# .schema users    - show table schema
# SELECT * FROM users;
# .quit            - exit

# Check file permissions
docker exec kasir-toko-sembako ls -la /app/instance
docker exec kasir-toko-sembako ls -la /app/backups

# Test HTTP endpoint
docker exec kasir-toko-sembako curl http://localhost:5000
```

## 📱 Port Management

```bash
# Check what's using port 5000
# Linux
sudo lsof -i :5000

# Windows PowerShell
Get-NetTCPConnection -LocalPort 5000

# Change port (edit docker-compose.yml)
# ports:
#   - "5001:5000"  # host:container
```

## 🔐 Security

```bash
# Update environment variables
docker-compose down
# Edit .env file
nano .env
docker-compose up -d

# Change passwords (run inside container)
docker exec -it kasir-toko-sembako python
>>> from app.app_simple import app, db, User
>>> with app.app_context():
...     user = User.query.filter_by(username='admin').first()
...     user.set_password('new-password')
...     db.session.commit()
```

## 📈 Performance

```bash
# Check memory usage
docker stats --no-stream kasir-toko-sembako

# Limit resources (edit docker-compose.yml)
# services:
#   kasir-app:
#     mem_limit: 512m
#     cpus: 1.0

# View logs without buffering
docker-compose logs -f --no-log-prefix
```

## 🌐 Network Access

```bash
# Access from local network
http://[IP-ADDRESS]:5000

# Find local IP
# Linux
hostname -I

# Windows PowerShell
Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "192.168.*"}

# Mac
ifconfig | grep "inet "
```

## 📦 Volumes

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect kasir-app_instance

# Backup volume
docker run --rm -v kasir-app_instance:/data -v $(pwd):/backup ubuntu tar czf /backup/instance-backup.tar.gz /data

# Restore volume
docker run --rm -v kasir-app_instance:/data -v $(pwd):/backup ubuntu tar xzf /backup/instance-backup.tar.gz -C /
```

## 🎯 Quick Commands

| Task | Command |
|------|---------|
| Start | `docker-compose up -d` |
| Stop | `docker-compose down` |
| Restart | `docker-compose restart` |
| Logs | `docker-compose logs -f` |
| Shell | `docker exec -it kasir-toko-sembako bash` |
| Status | `docker-compose ps` |
| Rebuild | `docker-compose up -d --build` |
| Update | `git pull && docker-compose up -d --build` |

## 🆘 Emergency

```bash
# App tidak respond
docker-compose restart

# Database corrupt
docker exec -it kasir-toko-sembako bash
cd /app/instance
# Restore from backup

# Port conflict
# Edit docker-compose.yml, change port
docker-compose down
docker-compose up -d

# Memory full
docker system prune -a
docker volume prune
```

## 📚 Useful Links

- Docker Docs: https://docs.docker.com/
- Docker Compose: https://docs.docker.com/compose/
- CasaOS Docs: https://casaos.io/
- Flask: https://flask.palletsprojects.com/

---

**💡 Tips:**
- Selalu backup sebelum update
- Monitor logs untuk early warning
- Set resource limits untuk stabilitas
- Gunakan .env untuk sensitive data
- Regular cleanup untuk free space
