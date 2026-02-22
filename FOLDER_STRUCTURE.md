# 📂 Struktur Folder - Kasir App

Workspace sudah dirapihkan! Berikut struktur folder yang bersih dan terorganisir:

## 🎯 Folder Utama (Produk)

### **customer_packages/**
**Paket siap kirim ke customer** - Ini yang Anda zip dan kirim ke pembeli
```
customer_packages/
├── windows/          → Untuk customer Windows
├── linux/            → Untuk customer Linux
├── macos/            → Untuk customer macOS
├── README_SELLER.md  → Panduan untuk Anda
└── README_GHCR.md    → Info tentang Docker image
```

**Isi setiap folder OS:**
- `docker-compose.localhost.yml` - Config Docker
- `.env.example` - Template environment (Anda edit license key-nya)
- `run.ps1` / `run.sh` / `run.command` - Script jalankan aplikasi
- `device_fingerprint.py` - Script generate fingerprint
- `README.md` - Panduan untuk customer

---

## 🔧 Folder Management (Anda)

### **_casaos_deploy/**
**Script untuk deploy/manage di CasaOS Anda**
```
_casaos_deploy/
├── deploy_quick.ps1              → Deploy license server (PAKAI INI!)
├── generate_customer_license.ps1 → Generate license via CLI
├── check_license_server_casaos.py → Cek status server
├── GENERATE_LICENSE_GUIDE.md     → Panduan lengkap
└── README.md                     → Dokumentasi folder ini
```

**Cara pakai:**
1. Buka PowerShell di folder ini: `cd _casaos_deploy`
2. Deploy license server: `.\deploy_quick.ps1`
3. Buka dashboard: http://192.168.1.25:8088/admin

### **_dev/**
**File development/testing** - Tidak perlu disentuh kecuali debugging
- Berisi 60+ file test/debug/check scripts
- Ignore saja kalau tidak lagi develop

---

## 🚀 Folder Aplikasi (Core)

### **app/**
Aplikasi kasir utama (Python Flask)
- Source code aplikasi
- Templates HTML
- Static files (CSS/JS)
- Config & license manager

### **license_server/**
Server aktivasi & monitoring license
- Server Flask untuk aktivasi
- Admin dashboard untuk monitoring
- Database SQLite untuk license
- **Sudah deployed di CasaOS port 8088**

### **.github/workflows/**
GitHub Actions untuk build Docker image
- `publish-ghcr.yml` - Auto build saat push tag v*.*.*
- Image: `ghcr.io/indralavansa/kasir-app:v1.0.0`

---

## 📚 Folder Support

### **migrations/**
Database migration scripts

### **scripts/**
Utility scripts (backup, migrate, dll)

### **tools/**
Additional tools & helpers

### **tests/**
Unit tests

### **docs/**
Dokumentasi tambahan

---

## 📄 File Penting Root

```
.
├── Dockerfile                → Build Docker image aplikasi
├── docker-compose.yml        → Run aplikasi lokal
├── requirements.txt          → Python dependencies
├── setup-docker.ps1/sh       → Setup Docker environment
├── README.md                 → Dokumentasi utama
├── START_HERE.md             → Quick start guide
├── QUICKSTART_CASAOS.md      → Panduan deploy ke CasaOS
├── CHANGELOG.md              → Version history
└── cleanup_workspace.ps1     → Script cleanup (sudah dijalankan)
```

---

## 🎯 Workflow Anda Sehari-hari

### Saat Ada Customer Beli:

1. **Generate License**
   ```
   Buka: http://192.168.1.25:8088/admin
   Login: admin / Lavansastore
   Klik: "Buat License Baru"
   Copy: License key yang muncul
   ```

2. **Siapkan Package untuk Customer**
   ```powershell
   # Copy folder sesuai OS customer
   cp -r customer_packages/windows customer_untuk_pak_budi
   
   # Edit .env.example
   # Isi KASIR_LICENSE_KEY=<key dari step 1>
   
   # Zip dan kirim
   ```

3. **Monitor Customer**
   ```
   Dashboard: http://192.168.1.25:8088/admin
   Lihat: Total devices, active users, last seen, dll
   ```

### Kalau Perlu Deploy/Update:

```powershell
# Deploy license server
cd _casaos_deploy
.\deploy_quick.ps1

# Deploy aplikasi utama
.\deploy-to-casaos.ps1
```

---

## 🗑️ File yang Sudah Dihapus

✅ File temporary/backup (BACKUP_*.txt, deployment_log.txt, dll)
✅ Folder duplikat (Connect to Telegram..., sale_package/, dll)
✅ File test yang scattered (dipindah ke _dev/)
✅ 60+ file testing/debugging (dipindah ke _dev/)

---

## 💡 Tips

- **Jangan edit** folder `_dev/` kecuali debugging
- **Fokus di** `customer_packages/` dan `_casaos_deploy/`
- **Dashboard** adalah cara termudah untuk manage license
- **Folder ini** sudah di-push ke GitHub (kecuali _dev/ yang di-ignore)

---

**Repository:** https://github.com/Indralavansa/Kasir-app
**GHCR Image:** ghcr.io/indralavansa/kasir-app:v1.0.0
**License Server:** http://192.168.1.25:8088/admin
