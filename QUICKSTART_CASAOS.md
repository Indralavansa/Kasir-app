# ⚡ QUICK START - STB HG680P + CasaOS

Panduan super cepat deploy dalam 5 menit!

## 📱 Langkah Singkat

### 1️⃣ Upload File ke STB
```
Transfer folder aplikasi ke:
/DATA/AppData/kasir-app/
```

**Cara transfer:**
- SMB/Samba via CasaOS Files app (recommended)
- SCP/SFTP via terminal
- USB drive → copy manual

### 2️⃣ Deploy via CasaOS UI

1. Buka CasaOS: `http://[IP-STB]`
2. Klik **App Store** → **"+"** (Custom Install)
3. Pilih **"Import from Docker Compose"**
4. Copy-paste isi `docker-compose.yml`
5. Klik **"Install"**
6. Tunggu build selesai (~2-3 menit)

### 3️⃣ Akses Aplikasi

```
URL: http://[IP-STB]:5000
```

**Login:**
- Admin: `admin` / `admin123`
- Kasir: `kasir` / `kasir123`

🎉 **Done!**

---

## 🔧 Deploy via Terminal (Alternative)

```bash
# SSH ke STB
ssh casaos@[IP-STB]

# Masuk ke folder app
cd /DATA/AppData/kasir-app

# Start container
docker-compose up -d

# Check logs
docker-compose logs -f
```

---

## 📊 Command Penting

| Task | Command |
|------|---------|
| **Start** | `docker-compose up -d` |
| **Stop** | `docker-compose down` |
| **Logs** | `docker-compose logs -f` |
| **Restart** | `docker-compose restart` |
| **Update** | `docker-compose up -d --build` |
| **Shell** | `docker exec -it kasir-toko-sembako bash` |

---

## ⚙️ Optional: Environment Variables

Edit `.env` untuk konfigurasi tambahan:

```bash
# Copy template
cp .env.example .env

# Edit
nano .env
```

**Setting penting:**
- `SECRET_KEY` - Ganti dengan random string
- `TELEGRAM_BOT_TOKEN` - Token bot (optional)
- `TELEGRAM_ADMIN_CHAT_IDS` - Chat ID admin (optional)

---

## 🔍 Troubleshooting Cepat

**Port 5000 conflict?**
```yaml
# Edit docker-compose.yml
ports:
  - "5001:5000"  # Ganti port
```

**Container tidak start?**
```bash
docker-compose logs -f
docker-compose restart
```

**Memory issue (RAM 2GB)?**
```yaml
# Tambah di docker-compose.yml
mem_limit: 512m
```

---

## 📚 Dokumentasi Lengkap

- [DEPLOYMENT_CASAOS.md](DEPLOYMENT_CASAOS.md) - Panduan detail
- [DOCKER_COMMANDS.md](DOCKER_COMMANDS.md) - Command reference
- [README.md](README.md) - Fitur aplikasi

---

## 💡 Tips

✅ Ganti password default setelah login
✅ Setup backup otomatis
✅ Monitor logs untuk error
✅ Test dari handphone di network yang sama
✅ Setup Telegram bot untuk remote monitoring

---

**Need help?** 
- Check logs: `docker-compose logs -f`
- Restart: `docker-compose restart`
- Full docs: `DEPLOYMENT_CASAOS.md`
