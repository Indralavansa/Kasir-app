# Tutorial GHCR (GitHub Container Registry)

Target: customer pakai `KASIR_IMAGE=ghcr.io/<owner>/<repo>:v1.0.0`

## 1) Buat repo GitHub (kalau belum ada)
1. Buka GitHub -> New repository
2. Nama repo contoh: `kasir-app`
3. Pilih Public (lebih gampang untuk customer pull tanpa login)
4. Create repository

## 2) Push source project ke repo
Di folder project ini:

```bash
git init
git add .
git commit -m "init"
git branch -M main
git remote add origin https://github.com/<owner>/<repo>.git
git push -u origin main
```

## 3) Workflow publish ke GHCR
File workflow sudah ada di:
- `.github/workflows/publish-ghcr.yml`

Workflow akan build & push image ke GHCR saat Anda push tag versi.

## 4) Buat rilis versi pertama (tag)
Contoh versi `v1.0.0`:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Tunggu GitHub Actions selesai.

## 5) Set image jadi public (sekali saja)
1. Buka GitHub repo -> Packages
2. Klik package image
3. Package settings -> Visibility -> Public

## 6) Isi `KASIR_IMAGE` di paket customer
Contoh:

```env
KASIR_IMAGE=ghcr.io/<owner>/<repo>:v1.0.0
```

Customer tinggal jalankan script `run` sesuai OS.

## Catatan
- Kalau repo/package private: customer harus `docker login ghcr.io` pakai PAT. Untuk jualan awal, Public lebih simpel.
