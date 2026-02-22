# Paket Customer - Windows

## Yang dibutuhkan
- Docker Desktop
- (Opsional) Python untuk generate fingerprint (atau pakai halaman `/license`)

## Cara jalan
1) Copy `.env.example` -> `.env`, isi variabel.
2) Buat `DEVICE_FINGERPRINT`:
   - Opsi cepat: jalankan `python device_fingerprint.py`
   - Atau buka `http://127.0.0.1:5000/license` nanti fingerprint tampil di sana.
3) Start:
   - Klik kanan `run.ps1` -> Run with PowerShell
   - atau jalankan: `powershell -ExecutionPolicy Bypass -File run.ps1`

Akses:
- http://127.0.0.1:5000

Jika lisensi belum aktif:
- http://127.0.0.1:5000/license

## Jika penjual kirim image offline
Penjual bisa kirim file `kasir-image.tar`.
Load:
- `docker load -i kasir-image.tar`
Lalu set `KASIR_IMAGE` di `.env` sesuai nama image yang diberikan penjual.
