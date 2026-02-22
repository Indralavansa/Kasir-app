# 🏁 START HERE - Deployment Guide

Pilih metode deployment yang sesuai dengan environment Anda.

## 🎯 Pilih Platform

### 1. 📦 STB HG680P + CasaOS (Recommended untuk STB)
**Cocok untuk:** Set-top box, NAS, Home server dengan CasaOS

**Quick Start:**
```bash
📖 Baca: QUICKSTART_CASAOS.md (5 menit)
📚 Detail: DEPLOYMENT_CASAOS.md
```

**Langkah singkat:**
1. Upload folder ke `/DATA/AppData/kasir-app/`
2. CasaOS → Import `docker-compose.yml`
3. Start container
4. Access: `http://[IP-STB]:5000`

---

### 2. 🐳 Docker / Linux Server
**Cocok untuk:** VPS, Linux server, Docker-enabled system

**Quick Setup:**
```bash
# Linux/Mac
bash setup-docker.sh

# Windows PowerShell
.\setup-docker.ps1
```

**Manual:**
```bash
docker-compose up -d
```

**Reference:**
- 📖 `DOCKER_COMMANDS.md` - Command cheat sheet
- 📚 `DEPLOYMENT_CASAOS.md` - Full guide

---

### 3. 💻 Windows/Linux (Native Python)
**Cocok untuk:** Development, PC/Laptop lokal

**Setup:**
```bash
# Install dependencies
pip install -r requirements.txt

# Run application
scripts\start_app.bat      # Windows
python app/app_simple.py   # Linux/Mac
```

**Access:** `http://localhost:5000`

**Docs:** `README.md` → Quick Start section

---

## 📚 File Documentation Map

```
├── START_HERE.md              ← 👋 You are here!
│
├── 🐳 Docker/CasaOS Deployment
│   ├── QUICKSTART_CASAOS.md   ← ⚡ Start here (5 min)
│   ├── DEPLOYMENT_CASAOS.md   ← 📖 Full guide
│   ├── DOCKER_COMMANDS.md     ← 🔧 Command reference
│   ├── DEPLOYMENT_FILES.md    ← 📦 File list & checklist
│   ├── docker-compose.yml     ← ⚙️ Compose config
│   ├── Dockerfile             ← 📦 Container image
│   ├── setup-docker.sh        ← 🛠️ Linux/Mac setup
│   └── setup-docker.ps1       ← 🛠️ Windows setup
│
├── 📱 Application Features
│   ├── README.md              ← 📖 Main readme & features
│   ├── docs/HARGA_VARIASI.md  ← 💰 Tier pricing
│   ├── docs/TELEGRAM_BOT.md   ← 📱 Telegram integration
│   └── docs/BACKUP_OTOMATIS.md← 💾 Auto backup
│
└── 📝 Others
    ├── CHANGELOG.md           ← 🗓️ Version history
    └── requirements.txt       ← 📦 Python dependencies
```

---

## ⚡ Quick Decision Guide

**Pertanyaan:** Dimana aplikasi akan dijalankan?

### → STB HG680P dengan CasaOS
```
✅ Baca: QUICKSTART_CASAOS.md
🛠️ File: docker-compose.yml
```

### → Linux server / VPS dengan Docker
```
✅ Run: bash setup-docker.sh
📖 Ref: DOCKER_COMMANDS.md
```

### → Windows PC untuk testing/development
```
✅ Run: scripts\start_app.bat
📖 Ref: README.md
```

### → Laptop Linux/Mac untuk development
```
✅ Run: python app/app_simple.py
📖 Ref: README.md
```

---

## 🎓 Learning Path

### Pemula (Baru pertama kali)
1. ✅ Baca `QUICKSTART_CASAOS.md` (5 min)
2. ✅ Deploy via CasaOS UI
3. ✅ Test akses aplikasi
4. ✅ Ganti password default
5. ✅ Baca `README.md` untuk fitur

### Intermediate (Sudah familiar Docker)
1. ✅ Review `docker-compose.yml`
2. ✅ Edit `.env` sesuai kebutuhan
3. ✅ Run `docker-compose up -d`
4. ✅ Bookmark `DOCKER_COMMANDS.md`
5. ✅ Setup Telegram bot (optional)

### Advanced (Custom deployment)
1. ✅ Customize `Dockerfile`
2. ✅ Setup reverse proxy (Nginx/Traefik)
3. ✅ Configure SSL/HTTPS
4. ✅ Setup monitoring (Grafana/Prometheus)
5. ✅ Implement CI/CD pipeline

---

## 🆘 Troubleshooting Path

**Problem:** Container tidak start
→ Check: `DEPLOYMENT_CASAOS.md` → Troubleshooting section

**Problem:** Port conflict
→ Check: `DOCKER_COMMANDS.md` → Port Management

**Problem:** Database error
→ Check: `README.md` → Troubleshooting section

**Problem:** Lupa command
→ Check: `DOCKER_COMMANDS.md` → Quick Commands table

---

## ✅ Post-Deployment Checklist

Setelah sukses deploy, lakukan:

- [ ] Akses aplikasi via browser
- [ ] Login dengan credentials default
- [ ] **⚠️ GANTI PASSWORD DEFAULT**
- [ ] Test tambah produk
- [ ] Test transaksi
- [ ] Verify backup berfungsi
- [ ] Test akses dari device lain
- [ ] Setup Telegram bot (optional)
- [ ] Bookmark dashboard
- [ ] Save credentials di password manager

---

## 📞 Support Resources

**Stuck?** Cek urutan ini:

1. 📖 `QUICKSTART_CASAOS.md` - Quick solutions
2. 📚 `DEPLOYMENT_CASAOS.md` - Detailed troubleshooting
3. 🔧 `DOCKER_COMMANDS.md` - Command help
4. 📝 Check logs: `docker-compose logs -f`
5. 🔄 Try restart: `docker-compose restart`

---

## 🎯 Goals by Platform

### STB HG680P Goal
- ✅ Running 24/7
- ✅ Low power consumption
- ✅ Auto-restart on crash
- ✅ Remote access via IP
- ✅ Backup to external storage

### Development Goal
- ✅ Quick start/stop
- ✅ Easy debugging
- ✅ Fast iteration
- ✅ Hot reload (optional)

### Production Server Goal
- ✅ High availability
- ✅ Resource monitoring
- ✅ Regular backups
- ✅ Security hardening
- ✅ HTTPS enabled

---

## 🚀 Ready to Start?

**For STB HG680P:** → Open `QUICKSTART_CASAOS.md`
**For Docker:** → Run `setup-docker.sh`
**For Development:** → Read `README.md`

---

**Version:** 1.1.0  
**Last Updated:** February 12, 2026  
**Platform Support:** Windows | Linux | Docker | CasaOS | ARM | x86

🎉 **Happy deploying!**
