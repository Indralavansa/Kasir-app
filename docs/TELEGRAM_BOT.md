# 📱 Telegram Bot - Panduan Lengkap

## Deskripsi
Bot Telegram memungkinkan Anda memantau kasir dari jarak jauh melalui aplikasi Telegram. Anda dapat melihat laporan penjualan, omzet, produk terlaris, top member, stok rendah, dan grafik penjualan harian.

## ✨ Fitur

### 1. **Laporan Real-time**
- 📊 Laporan Hari Ini - Total transaksi dan omzet
- 💰 Omzet Hari Ini - Detail pendapatan per metode pembayaran
- 🏆 Produk Terlaris - Top 10 produk yang paling laku
- 👥 Top Member - Top 10 member berdasarkan total pembelanjaan
- ⚠️ Stok Rendah - Produk dengan stok di bawah threshold
- 📈 Grafik Penjualan - Visualisasi penjualan 7 hari terakhir

### 2. **Notifikasi Otomatis**
- 🔔 Notifikasi transaksi baru (opsional)
- 📦 Alert stok rendah (opsional)

### 3. **Keamanan**
- 🔒 Hanya admin yang bisa menggunakan bot
- 🔑 Validasi Chat ID untuk setiap perintah

## 🚀 Setup Bot Telegram

### Langkah 1: Buat Bot di Telegram

1. **Buka Telegram** dan cari `@BotFather`
2. **Kirim perintah** `/newbot`
3. **Masukkan nama bot** (contoh: `Kasir Monitor Bot`)
4. **Masukkan username bot** (harus diakhiri dengan "bot", contoh: `kasirmonitor_bot`)
5. **Simpan Token Bot** yang diberikan oleh BotFather
   - Format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567`

### Langkah 2: Dapatkan Chat ID Admin

#### Cara 1: Menggunakan Bot
1. **Cari bot Anda** di Telegram menggunakan username yang dibuat
2. **Kirim pesan** `/start` ke bot Anda
3. **Buka browser** dan kunjungi:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
   Ganti `<YOUR_BOT_TOKEN>` dengan token dari BotFather
4. **Cari "chat"** dalam response JSON, lihat nilai `"id":`
   - Contoh response:
   ```json
   {
     "ok": true,
     "result": [{
       "update_id": 123456789,
       "message": {
         "message_id": 1,
         "from": {"id": 987654321, "is_bot": false, "first_name": "Your Name"},
         "chat": {"id": 987654321, "first_name": "Your Name", "type": "private"},
         "date": 1234567890,
         "text": "/start"
       }
     }]
   }
   ```
   Chat ID Anda adalah: `987654321`

#### Cara 2: Menggunakan @userinfobot
1. **Cari** `@userinfobot` di Telegram
2. **Kirim pesan** apa saja ke bot tersebut
3. **Bot akan membalas** dengan informasi Anda, termasuk Chat ID

### Langkah 3: Konfigurasi Aplikasi

1. **Salin file `.env.example`** menjadi `.env`:
   ```bash
   copy .env.example .env
   ```

2. **Edit file `.env`** dan isi konfigurasi Telegram:
   ```env
   # Telegram Bot Configuration
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567
   TELEGRAM_ADMIN_CHAT_IDS=987654321,123456789
   TELEGRAM_NOTIFY_NEW_TRANSACTION=True
   TELEGRAM_NOTIFY_LOW_STOCK_THRESHOLD=10
   ```

   **Penjelasan:**
   - `TELEGRAM_BOT_TOKEN`: Token bot dari BotFather
   - `TELEGRAM_ADMIN_CHAT_IDS`: Chat ID admin (pisahkan dengan koma jika lebih dari satu)
   - `TELEGRAM_NOTIFY_NEW_TRANSACTION`: `True` untuk mengaktifkan notifikasi transaksi baru
   - `TELEGRAM_NOTIFY_LOW_STOCK_THRESHOLD`: Batas stok untuk alert (default: 10)

### Langkah 4: Install Dependencies

Jalankan perintah berikut untuk menginstall library Telegram:
```bash
pip install -r requirements.txt
```

### Langkah 5: Jalankan Aplikasi

Jalankan aplikasi seperti biasa:
```bash
python app/app_simple.py
```

Jika konfigurasi benar, Anda akan melihat pesan:
```
🤖 Telegram Bot Configuration:
   ✓ Token: Present
   ✓ Admin Chat IDs: 1 configured
   ✓ Bot started successfully in background
```

Jika ada error, pesan error akan ditampilkan.

## 📱 Cara Menggunakan Bot

### Perintah Bot

1. **Buka bot Anda** di Telegram
2. **Kirim perintah** `/start` untuk melihat menu utama
3. **Klik tombol** untuk melihat laporan:
   - 📊 **Laporan Hari Ini**: Ringkasan transaksi dan omzet
   - 💰 **Omzet Hari Ini**: Detail pendapatan per metode pembayaran
   - 🏆 **Produk Terlaris**: Top 10 produk paling laku
   - 👥 **Top Member**: Top 10 member terbesar
   - ⚠️ **Stok Rendah**: Produk dengan stok menipis
   - 📈 **Grafik Penjualan**: Chart penjualan 7 hari

### Contoh Laporan

#### Laporan Hari Ini
```
📊 LAPORAN HARI INI
Jumat, 7 Februari 2025

💰 Total Transaksi: 25
💵 Total Omzet: Rp 2.500.000

💳 Tunai: Rp 1.800.000 (18 transaksi)
💳 QRIS: Rp 700.000 (7 transaksi)

🕐 Dibuat: 10:30:25
```

#### Produk Terlaris
```
🏆 PRODUK TERLARIS HARI INI
Jumat, 7 Februari 2025

1. Indomie Goreng
   📦 15 terjual | 💰 Rp 45.000

2. Aqua 600ml
   📦 12 terjual | 💰 Rp 36.000

3. Beras Premium 5kg
   📦 8 terjual | 💰 Rp 400.000

🕐 Dibuat: 10:30:25
```

#### Stok Rendah
```
⚠️ STOK RENDAH
Jumat, 7 Februari 2025

1. Indomie Goreng
   📦 Stok: 5 pcs

2. Aqua 600ml
   📦 Stok: 8 pcs

3. Gula Pasir 1kg
   📦 Stok: 3 pcs

🕐 Dibuat: 10:30:25
```

### Notifikasi Otomatis

Jika diaktifkan, bot akan mengirim notifikasi:

#### Transaksi Baru
```
🔔 TRANSAKSI BARU

🧾 Kode: TRX20250207103045
💰 Total: Rp 125.000
💳 Metode: Tunai
👤 Kasir: Admin
👥 Member: John Doe

⏰ 10:30:45
```

#### Stok Rendah
```
⚠️ PERINGATAN STOK RENDAH!

📦 Produk: Indomie Goreng
📊 Stok Tersisa: 5 pcs
📁 Kategori: Makanan

Segera lakukan restock!
```

## ⚙️ Konfigurasi Lanjutan

### Mengubah Batas Stok Rendah
Edit `.env`:
```env
TELEGRAM_NOTIFY_LOW_STOCK_THRESHOLD=15
```
Stok akan memberikan alert jika <= 15.

### Mematikan Notifikasi Transaksi
Edit `.env`:
```env
TELEGRAM_NOTIFY_NEW_TRANSACTION=False
```

### Menambah Multiple Admin
Pisahkan Chat ID dengan koma:
```env
TELEGRAM_ADMIN_CHAT_IDS=987654321,123456789,555666777
```

### Menghapus Bot (Opsional)
Jika tidak menggunakan bot, hapus atau kosongkan:
```env
TELEGRAM_BOT_TOKEN=
```

## 🔧 Troubleshooting

### Bot Tidak Merespon
1. **Cek token bot** di `.env` sudah benar
2. **Pastikan Chat ID** sudah terdaftar di admin
3. **Cek koneksi internet** server
4. **Lihat log aplikasi** untuk pesan error

### Notifikasi Tidak Muncul
1. **Cek konfigurasi** `TELEGRAM_NOTIFY_NEW_TRANSACTION` di `.env`
2. **Pastikan threshold** `TELEGRAM_NOTIFY_LOW_STOCK_THRESHOLD` sudah sesuai
3. **Cek log aplikasi** saat checkout untuk melihat status pengiriman

### Error saat Startup
```
❌ Bot failed to start: Unauthorized
```
**Solusi**: Token bot salah atau tidak valid. Dapatkan token baru dari @BotFather.

```
⚠ No admin Chat IDs configured
```
**Solusi**: Tambahkan Chat ID admin di `.env`.

### Error Dependencies
```
ModuleNotFoundError: No module named 'telegram'
```
**Solusi**: Install dependencies:
```bash
pip install python-telegram-bot==20.8
```

## 🛡️ Keamanan

1. **Jangan share token bot** kepada orang lain
2. **Simpan file `.env`** di `.gitignore` jika menggunakan Git
3. **Hanya tambahkan Chat ID** orang yang dipercaya sebagai admin
4. **Bot hanya merespon** Chat ID yang terdaftar di konfigurasi
5. **Gunakan HTTPS** jika deploy ke server public

## 📝 Tips

1. **Tambahkan bot ke grup** (opsional):
   - Tambahkan bot ke grup Telegram
   - Dapatkan Group Chat ID menggunakan getUpdates
   - Tambahkan Group Chat ID ke `TELEGRAM_ADMIN_CHAT_IDS`

2. **Gunakan perintah `/help`** untuk melihat panduan cepat

3. **Monitor stok** secara berkala dengan tombol "⚠️ Stok Rendah"

4. **Grafik penjualan** membantu melihat tren penjualan 7 hari terakhir

5. **Top Member** membantu identifikasi pelanggan setia untuk program loyalitas

## 🆘 Support

Jika mengalami masalah:
1. Cek file log aplikasi
2. Cek dokumentasi di `docs/`
3. Pastikan semua dependencies terinstall
4. Verifikasi konfigurasi di `.env`

---

**Happy Monitoring! 🚀**
