# Paket Customer - Linux

## Yang dibutuhkan
- Docker Engine + Docker Compose plugin
- (Opsional) Python untuk generate fingerprint

## Cara jalan
1) Copy `.env.example` -> `.env`, isi variabel.
2) Buat `DEVICE_FINGERPRINT`:
   - `python3 device_fingerprint.py`
   - atau lihat di `http://127.0.0.1:5000/license`
3) Start:
   - `chmod +x run.sh`
   - `./run.sh`

Akses:
- http://127.0.0.1:5000

## Image offline
Kalau penjual kirim `kasir-image.tar`:
- `docker load -i kasir-image.tar`
- set `KASIR_IMAGE` di `.env`
