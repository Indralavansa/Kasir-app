# CasaOS Deployment Scripts

Folder ini berisi script untuk deploy dan manage aplikasi di CasaOS Anda (192.168.1.25).

## Quick Deploy License Server

**Cara tercepat:**
```powershell
.\deploy_quick.ps1
```

## Script yang Tersedia

### Deploy Scripts
- **deploy_quick.ps1** - Deploy license server (RECOMMENDED)
- **deploy-to-casaos.ps1** - Deploy aplikasi kasir utama
- **deploy_license_server_now.ps1** - Deploy license server (detailed)
- **deploy_license_server_casaos.py** - Python version
- **deploy_license_ui_hotfix.py** - Hotfix untuk UI license server

### License Management
- **generate_customer_license.ps1** - Generate license via command line
- **create_license_on_casaos.py** - Create license di CasaOS
- **generate_license_keys.py** - Generate ED25519 keys untuk signing

### Monitoring & Maintenance
- **check_license_server_casaos.py** - Cek status license server
- **check_license_server_container.py** - Cek container license server
- **get_license_server_logs.py** - Ambil logs license server
- **get_server_logs.py** - Ambil logs server umum
- **restart_license_server_casaos.py** - Restart license server

## Configuration
- **casaos-config.json** - Konfigurasi CasaOS
- **GENERATE_LICENSE_GUIDE.md** - Panduan lengkap generate license

## Quickstart

### 1. Deploy License Server
```powershell
.\deploy_quick.ps1
```

### 2. Buka Dashboard
```
http://192.168.1.25:8088/admin
Username: admin
Password: Lavansastore
```

### 3. Generate License
Buka dashboard → Klik "Buat License Baru" → Pilih tier → Generate!

## Notes

- Semua script membutuhkan SSH access ke `root@192.168.1.25`
- Password root akan diminta saat deploy
- License server berjalan di port **8088**
- Aplikasi utama berjalan di port **8080**
