# Customer Packages (Per-OS)

Folder yang siap Anda kirim ke customer sesuai OS:
- `customer_packages/windows`
- `customer_packages/linux`
- `customer_packages/macos`

## Isi paket (semua OS)
- `docker-compose.localhost.yml`
- `.env.example`
- script run sesuai OS (`run.ps1` / `run.sh` / `run.command`)
- `device_fingerprint.py`
- `README.md`

## Cara Kirim ke Customer

### 1. Docker Image (Sudah Otomatis) ✅
Image sudah tersedia di GitHub Container Registry:
```
ghcr.io/indralavansa/kasir-app:v1.0.0
```

**Sudah diisi di semua `.env.example`** - Customer tinggal pakai!

**PENTING:** Pastikan package visibility GHCR sudah **Public**:
- Buka: https://github.com/users/Indralavansa/packages/container/kasir-app/settings
- Change visibility → **Public**
- Kalau masih Private, customer tidak bisa pull image!

### 2. Generate License untuk Customer
Di CasaOS Anda (192.168.1.25), generate license:
```bash
# SSH ke CasaOS atau lewat container
docker exec -it license-server python admin_create_license.py standard
docker exec -it license-server python admin_create_license.py pro
docker exec -it license-server python admin_create_license.py unlimited
docker exec -it license-server python admin_create_license.py trial --days 30
```

### 3. Yang Perlu Dikirim ke Customer
Kirim folder sesuai OS customer (`windows/` atau `linux/` atau `macos/`) plus info ini:

**A) License Key** (dari step 2)
```
KASIR_LICENSE_KEY=<hasil generate>
```

**B) Public Key Server** (agar customer bisa verifikasi license):
```
LICENSE_SERVER_PUBLIC_KEY_B64=FubZG4q/E7a8W9V1Ys6bYoZKPQYv7iYPq6S1Ay8phII=
```

**C) License Server URL** (sudah diisi default):
```
LICENSE_SERVER_URL=http://192.168.1.25:8088
```

Customer tinggal:
1. Edit `.env.example` → isi 3 nilai di atas
2. Rename jadi `.env`
3. Jalankan `run.ps1` (Windows) atau `run.sh` (Linux) atau `run.command` (macOS)
4. Buka browser → `http://localhost:8080`

### 4. Monitoring Customer
Pantau penggunaan customer di: http://192.168.1.25:8088/admin
- Username: `admin`
- Password: `Lavansastore`

Dashboard akan menampilkan:
- Total lisensi aktif
- Device yang online (24 jam / 7 hari terakhir)
- Breakdown per tier (Trial/Standard/Pro/Unlimited)
- Aktivitas terakhir (IP, versi app, last seen)
