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

## Yang perlu Anda siapkan sebagai penjual
Paket ini menjalankan aplikasi dari Docker image, jadi Anda harus menyediakan salah satu:

1) Registry image (disarankan)
- Beri customer nilai `KASIR_IMAGE` (contoh GHCR: `ghcr.io/<owner>/<repo>:v1.0.0`)
- Customer tinggal `docker pull ...` lalu run

2) Offline image tar
- Anda buat: `docker save -o kasir-image.tar <image:tag>`
- Kirim file `kasir-image.tar` ke customer
- Customer: `docker load -i kasir-image.tar`
- Lalu isi `KASIR_IMAGE` sesuai nama image

## License
- Anda generate key di CasaOS:
  - `python create_license_on_casaos.py standard|pro|unlimited`
  - `python create_license_on_casaos.py trial --days 30`
- Customer isi `KASIR_LICENSE_KEY` di `.env`

## Monitoring
Pastikan server lisensi Anda reachable dari customer (LAN/WAN) karena aktivasi + ping butuh akses ke `LICENSE_SERVER_URL`.
