# 🚀 Cara Generate License untuk Customer (via CasaOS)

## Langkah Cepat

### 1. Cek Status License Server
```powershell
python check_license_server_casaos.py
```

Kalau container sudah jalan ✅, lanjut ke step 2.  
Kalau belum ❌, ikuti **Setup Awal** di bawah.

---

### 2. Generate License (Container Sudah Jalan)

**Opsi A - Pakai Script PowerShell (MUDAH!):**
```powershell
# Standard (1 device, tanpa Telegram)
.\generate_customer_license.ps1 standard

# Trial 30 hari
.\generate_customer_license.ps1 trial 30

# Pro (1 device, dengan Telegram)
.\generate_customer_license.ps1 pro

# Unlimited (1 device, Telegram + auto updates)
.\generate_customer_license.ps1 unlimited
```

**Opsi B - Manual via SSH:**
```bash
# SSH ke CasaOS
ssh root@192.168.1.25

# Generate license
docker exec kasir-license-server python admin_create_license.py standard
docker exec kasir-license-server python admin_create_license.py trial --days 30
docker exec kasir-license-server python admin_create_license.py pro
docker exec kasir-license-server python admin_create_license.py unlimited
```

Output akan seperti ini:
```
LICENSE_KEY: ABCDE-FG123-HJK45-MNP67
```

---

### 3. Kirim ke Customer

Setelah dapat license key, kirim ke customer:

**Folder:** `customer_packages/windows/` (atau linux/macos sesuai OS customer)

**Info yang harus diisi di `.env`:**
```env
KASIR_IMAGE=ghcr.io/indralavansa/kasir-app:v1.0.0
LICENSE_SERVER_URL=http://192.168.1.25:8088
LICENSE_SERVER_PUBLIC_KEY_B64=FubZG4q/E7a8W9V1Ys6bYoZKPQYv7iYPq6S1Ay8phII=
KASIR_LICENSE_KEY=ABCDE-FG123-HJK45-MNP67
```

**Customer tinggal:**
1. Edit `.env.example` → isi nilai di atas
2. Rename jadi `.env`
3. Jalankan `run.ps1` (Windows) / `run.sh` (Linux) / `run.command` (macOS)
4. Buka browser: `http://localhost:8080`

---

## 🔧 Setup Awal (Kalau License Server Belum Jalan)

### Deploy License Server ke CasaOS

**Dari PC Anda (Windows):**

```powershell
# 1. Copy folder license_server ke CasaOS
scp -r license_server root@192.168.1.25:~/

# 2. SSH ke CasaOS
ssh root@192.168.1.25

# 3. Deploy container
cd ~/license_server
docker compose -f docker-compose.casaos.yml up -d --build

# 4. Cek logs (pastikan tidak ada error)
docker logs kasir-license-server

# 5. Test akses
curl http://localhost:8088/admin
```

Kalau berhasil, seharusnya muncul halaman login.

---

### Generate Signing Keys (Kalau Belum Ada)

Kalau di `license_server/.env` belum ada `LICENSE_SIGNING_KEY_B64`, generate dulu:

```bash
# Generate keys
python -c "from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey; import base64; k=Ed25519PrivateKey.generate(); pk=k.public_key().public_bytes_raw(); sk=k.private_bytes_raw(); print('PUBLIC_KEY_B64=',base64.b64encode(pk).decode()); print('PRIVATE_KEY_B64=',base64.b64encode(sk).decode())"
```

Output:
```
PUBLIC_KEY_B64= <copy ini untuk customer>
PRIVATE_KEY_B64= <copy ini untuk LICENSE_SIGNING_KEY_B64>
```

Edit `license_server/.env`:
```env
LICENSE_SIGNING_KEY_B64=<PRIVATE_KEY_B64 dari atas>
ADMIN_USER=admin
ADMIN_PASS=Lavansastore
FLASK_SECRET_KEY=<random string panjang>
```

Restart container:
```bash
cd ~/license_server
docker compose -f docker-compose.casaos.yml restart
```

---

## 🎯 Monitor Customer

**Admin Dashboard:**
- URL: http://192.168.1.25:8088/admin
- Login: `admin` / `Lavansastore`

Dashboard menampilkan:
- Total lisensi aktif
- Device online (24 jam / 7 hari)
- Breakdown per tier
- IP address customer
- Last seen / last ping

---

## 💡 Tips

**Kalau SSH ribet (minta password terus):**
```powershell
# Generate SSH key (sekali aja)
ssh-keygen

# Copy ke CasaOS
ssh-copy-id root@192.168.1.25

# Sekarang SSH tanpa password!
```

**Kalau customer tidak bisa akses LICENSE_SERVER_URL dari luar jaringan:**
- Setup port forwarding di router: `8088` → CasaOS
- Atau pakai VPN (Tailscale/ZeroTier)
- Atau customer harus dalam jaringan yang sama (LAN)

**Kalau mau lihat semua license yang sudah dibuat:**
```bash
ssh root@192.168.1.25
docker exec kasir-license-server sqlite3 /data/license_server.sqlite "SELECT license_key, tier, issued_at, expires_at FROM licenses"
```
