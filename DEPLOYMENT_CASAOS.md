# 🚀 Deployment ke STB HG680P dengan CasaOS

Panduan lengkap untuk menjalankan aplikasi Kasir Toko Sembako di STB HG680P menggunakan CasaOS.

## 📋 Prasyarat

### Hardware
- **STB HG680P** dengan spesifikasi:
  - CPU: Amlogic S905X (Quad-core ARM Cortex-A53)
  - RAM: 2GB atau lebih (recommended 4GB)
  - Storage: Minimal 8GB free space
  - Network: Ethernet atau WiFi dengan koneksi internet

### Software
- **CasaOS** sudah terinstall di STB HG680P
- **Docker** dan **Docker Compose** (biasanya sudah include dengan CasaOS)
- SSH access ke STB (optional, untuk troubleshooting)

## 🔧 Persiapan File

### 1. Transfer File ke STB
Ada beberapa cara untuk transfer file:

#### Opsi A: Menggunakan SMB/Samba (Recommended)
1. Buka **CasaOS** di browser: `http://[IP-STB]:80`
2. Masuk ke **Files** app
3. Upload folder aplikasi atau gunakan SMB share

#### Opsi B: Menggunakan SCP/SFTP
```bash
# Dari computer Windows (PowerShell)
scp -r "d:\Connect to Telegram Original - Copy" casaos@[IP-STB]:/DATA/AppData/kasir-app/
```

#### Opsi C: Menggunakan USB Drive
1. Copy folder aplikasi ke USB drive
2. Colokkan USB ke STB
3. Copy dari USB ke `/DATA/AppData/kasir-app/`

### 2. Struktur Folder di STB
Recommended path di CasaOS:
```
/DATA/AppData/kasir-app/
├── app/
├── backups/
├── data/
├── instance/
├── migrations/
├── scripts/
├── templates/
├── static/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env
```

## 🐳 Deployment dengan Docker Compose

### Metode 1: Menggunakan CasaOS UI (Paling Mudah)

#### 1. Buka CasaOS App Store
- URL: `http://[IP-STB]`
- Login dengan credential CasaOS Anda

#### 2. Custom Install
1. Klik **"+"** atau **"Custom Install"**
2. Pilih **"Import from Docker Compose"**
3. Paste isi file `docker-compose.yml`
4. Klik **"Install"**

#### 3. Konfigurasi Environment Variables
Di CasaOS UI, set environment variables jika perlu:
- `SECRET_KEY`: Ganti dengan random string
- `TELEGRAM_BOT_TOKEN`: Token dari BotFather (optional)
- `TELEGRAM_ADMIN_CHAT_IDS`: Chat ID admin (optional)

### Metode 2: Menggunakan Terminal/SSH

#### 1. SSH ke STB
```bash
ssh casaos@[IP-STB]
# Default password: casaos (atau sesuai setup Anda)
```

#### 2. Navigasi ke Folder Aplikasi
```bash
cd /DATA/AppData/kasir-app
```

#### 3. Setup Environment Variables (Optional)
```bash
# Copy dan edit .env
cp .env.example .env
nano .env   # atau vi .env
```

Edit file `.env`:
```bash
SECRET_KEY=ganti-dengan-random-string-yang-panjang
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_ADMIN_CHAT_IDS=123456789
```

#### 4. Build dan Run Container
```bash
# Build image
docker-compose build

# Start container
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## 🌐 Akses Aplikasi

### Dari Browser
- **Lokal (di STB)**: `http://localhost:5000`
- **Dari network lokal**: `http://[IP-STB]:5000`

Contoh: `http://192.168.1.100:5000`

### Login Default
```
Admin:
- Username: admin
- Password: admin123

Kasir:
- Username: kasir
- Password: kasir123
```

> ⚠️ **PENTING**: Segera ganti password default setelah login pertama!

## 🔍 Troubleshooting

### Container Tidak Start
```bash
# Check logs
docker-compose logs -f kasir-app

# Check container status
docker ps -a

# Restart container
docker-compose restart

# Rebuild jika ada perubahan
docker-compose down
docker-compose up -d --build
```

### Port Sudah Digunakan
Jika port 5000 sudah digunakan, edit `docker-compose.yml`:
```yaml
ports:
  - "5001:5000"  # Ganti 5001 dengan port lain
```

### Database Error
```bash
# Masuk ke container
docker exec -it kasir-toko-sembako bash

# Check database
cd instance
ls -la

# Reset database (HATI-HATI: akan hapus semua data!)
rm kasir.db
# Restart container untuk recreate
```

### Memory Issues di STB 2GB RAM
Jika STB hanya punya 2GB RAM, tambahkan memory limit di `docker-compose.yml`:
```yaml
services:
  kasir-app:
    build: .
    mem_limit: 512m
    memswap_limit: 1g
```

## 📊 Monitoring

### Check Resource Usage
```bash
# CPU & Memory usage
docker stats kasir-toko-sembako

# Disk usage
docker system df
docker volume ls
```

### Backup Management
```bash
# Masuk ke container
docker exec -it kasir-toko-sembako bash

# Run backup script (dari dalam container)
cd /app
python tools/backup_otomatis_standalone.py
```

Backup otomatis akan tersimpan di:
- Host: `/DATA/AppData/kasir-app/backups/`
- Container: `/app/backups/`

## 🔄 Update Aplikasi

### Update dengan Docker
```bash
cd /DATA/AppData/kasir-app

# Backup data dulu
docker-compose exec kasir-app python tools/backup_otomatis_standalone.py

# Pull update (jika dari git)
git pull

# Rebuild dan restart
docker-compose down
docker-compose up -d --build
```

## 🛡️ Security Recommendations

1. **Ganti Secret Key** di `.env` dengan random string
2. **Ganti Password Default** untuk admin dan kasir
3. **Setup Firewall** jika STB exposed ke internet:
   ```bash
   # Hanya allow dari local network
   sudo ufw allow from 192.168.1.0/24 to any port 5000
   ```
4. **Regular Backup** - setup scheduled backup via CasaOS Task
5. **HTTPS** - gunakan reverse proxy (Nginx/Caddy) jika perlu

## 📱 Akses dari Handphone

### Di Network Lokal yang Sama
1. Pastikan HP terhubung ke WiFi yang sama dengan STB
2. Buka browser di HP
3. Akses: `http://[IP-STB]:5000`

### Dari Luar (Internet)
Gunakan salah satu:
1. **Tailscale** - VPN untuk remote access (recommended)
2. **Cloudflare Tunnel** - expose ke internet secara aman
3. **Port Forwarding** - di router (less secure)

Setup Tailscale di CasaOS:
```bash
# Install Tailscale di CasaOS
# Ikuti dokumentasi Tailscale untuk ARM devices
# Setelah connect, access via: http://[tailscale-ip]:5000
```

## 🚿 Clean Up / Uninstall

```bash
# Stop dan remove container
docker-compose down

# Remove image
docker rmi kasir-toko-sembako

# Hapus semua data (HATI-HATI!)
cd /DATA/AppData
rm -rf kasir-app

# Clean up unused Docker resources
docker system prune -a
```

## 📞 Support

Jika mengalami masalah:
1. Check logs: `docker-compose logs -f`
2. Check documentation di folder `docs/`
3. Restart container: `docker-compose restart`
4. Rebuild: `docker-compose up -d --build`

## ⚡ Performance Tips untuk STB

### 1. Optimize Docker
```bash
# Edit /etc/docker/daemon.json
{
  "storage-driver": "overlay2",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

### 2. Reduce Memory Usage
- Matikan fitur Telegram bot jika tidak digunakan
- Limit backup retention (MAX_BACKUPS di config)
- Clear old logs regularly

### 3. Use SSD/Fast Storage
- Jika memungkinkan, install CasaOS di SSD eksternal
- Atau gunakan USB 3.0 drive untuk Docker volumes

## 🎯 Kesimpulan

Setelah setup selesai:
- ✅ Aplikasi running di `http://[IP-STB]:5000`
- ✅ Data persistent di volumes
- ✅ Auto-restart jika container crash
- ✅ Backup otomatis sesuai schedule
- ✅ Resource-efficient untuk STB

**Selamat menggunakan! 🎉**
