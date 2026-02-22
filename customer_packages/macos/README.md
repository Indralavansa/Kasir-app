# Paket Customer - macOS

## Yang dibutuhkan
- Docker Desktop
- (Opsional) Python 3

## Cara jalan
1) Copy `.env.example` -> `.env`, isi variabel.
2) Buat `DEVICE_FINGERPRINT`:
   - `python3 device_fingerprint.py`
   - atau lihat di `http://127.0.0.1:5000/license`
3) Start:
   - Klik 2x `run.command` (kalau diblok, buka Terminal: `chmod +x run.command` lalu jalankan).

Akses:
- http://127.0.0.1:5000
