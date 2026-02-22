# License Server (Activation)

Server ini dipakai untuk aktivasi online (1 license = 1 device) dan untuk validasi trial 30 hari berdasarkan tanggal dibuat.

Tambahan: server ini juga menyediakan website admin untuk memantau jumlah user/device yang aktif.

## Quick start

1) Buat signing key Ed25519

Jalankan di Python (lokal):

```bash
python -c "from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey; import base64; k=Ed25519PrivateKey.generate(); pk=k.public_key().public_bytes_raw(); sk=k.private_bytes_raw(); print('PUBLIC_KEY_B64=',base64.b64encode(pk).decode()); print('PRIVATE_KEY_B64=',base64.b64encode(sk).decode())"
```

2) Set env

- `LICENSE_SIGNING_KEY_B64` = PRIVATE_KEY_B64
- `LICENSE_DB` = path sqlite (default: `license_server.sqlite`)

3) Run

```bash
pip install flask cryptography
python server.py
```

Endpoint:
- `POST /api/activate` { license_key, device_fingerprint }

## Admin dashboard (monitoring)

Set env:
- `ADMIN_USER`
- `ADMIN_PASS`
- `FLASK_SECRET_KEY`

Buka:
- `/admin` (login)
- `/admin/dashboard` (monitor)

Dashboard menampilkan total license, total device, aktif 24 jam/7 hari, breakdown per tier, dan aktivitas terbaru.

## Ping / last_seen

Endpoint:
- `POST /api/ping` { license_key, device_fingerprint, app_version }

Jika aplikasi customer mengaktifkan `LICENSE_PING=true`, maka `last_seen` akan ter-update sehingga Anda bisa melihat customer yang masih aktif.

## Deploy di CasaOS (Docker Compose)

Gunakan file `docker-compose.casaos.yml` dan jalankan:

```bash
cd license_server
docker compose -f docker-compose.casaos.yml up -d --build
```

Lalu akses:
- `http://IP_CASAOS:8088/admin`

Catatan: public key (`PUBLIC_KEY_B64`) harus diset juga di aplikasi sebagai `LICENSE_SERVER_PUBLIC_KEY_B64`.
