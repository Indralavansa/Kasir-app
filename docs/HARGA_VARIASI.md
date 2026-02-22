# Sistem Harga Variasi (Tier Pricing)

## Deskripsi
Sistem harga variasi memungkinkan Anda mengatur harga berbeda berdasarkan jumlah pembelian. Semakin banyak yang dibeli, harga per unit bisa lebih murah.

## Contoh Penggunaan
Untuk produk "Beras Premium":
- 1-9 kg = Rp 15.000/kg (harga normal)
- 10-49 kg = Rp 14.000/kg (diskon 1.000)
- 50-99 kg = Rp 13.500/kg (diskon 1.500)
- 100+ kg = Rp 13.000/kg (diskon 2.000)

## Cara Setup

### 1. Jalankan Migration (WAJIB untuk database lama)
Jalankan file batch berikut untuk menambahkan tabel harga variasi:
```
scripts\migrate_harga_variasi.bat
```

Migration ini akan:
- Membuat tabel `harga_variasi` 
- Migrasi data harga grosir lama ke sistem baru
- Membuat index untuk performa optimal

### 2. Menambah/Edit Harga Variasi di Produk

#### Saat Tambah Produk Baru:
1. Buka menu **Produk** > **Tambah Produk**
2. Isi data produk seperti biasa
3. Di bagian **"Harga Variasi (Tier Pricing)"**, klik **"Tambah Tier Harga"**
4. Masukkan:
   - **Minimal Quantity**: Jumlah minimal untuk dapat harga ini
   - **Harga per Unit**: Harga per item pada tier ini
   - **Keterangan**: Label opsional (misal: "Grosir", "Super Hemat", dll)
5. Tambahkan tier sebanyak yang dibutuhkan
6. Klik **"Simpan"**

#### Saat Edit Produk:
1. Buka menu **Produk** > Klik tombol **Edit** (ikon pensil)
2. Scroll ke bagian **"Harga Variasi (Tier Pricing)"**
3. Harga variasi yang sudah ada akan muncul
4. Untuk menghapus tier: klik tombol merah (ikon trash)
5. Untuk menambah tier baru: klik **"Tambah Tier Harga"**
6. Klik **"Simpan"**

### 3. Transaksi dengan Harga Variasi

#### Di Kasir:
1. Product card akan menampilkan semua tier harga yang tersedia
2. Saat menambahkan produk ke keranjang, sistem otomatis menggunakan **harga normal**
3. Saat quantity ditambah:
   - Sistem **otomatis menghitung** tier mana yang cocok
   - Harga per unit akan **berubah otomatis** sesuai tier
   - Badge hijau akan muncul menunjukkan tier aktif (misal: "Tier 10+")
4. Total otomatis dikalkulasi: `quantity × harga_tier`

## Tips & Best Practices

### ✅ Tips Mengatur Tier:
1. **Urutkan dari terkecil**: Mulai dari qty terkecil ke terbesar
2. **Buat tier yang masuk akal**: 
   - ❌ Buruk: 1, 2, 3, 4, 5... (terlalu banyak tier)
   - ✅ Baik: 1, 10, 50, 100 (tier yang logis)
3. **Gunakan keterangan yang jelas**: "Grosir", "Super Hemat", "Partai Besar"

### ⚠️ Perhatian:
- Sistem akan **otomatis memilih harga terendah** yang sesuai dengan qty
- Jika ada 2 tier dengan min_qty sama, yang terakhir akan digunakan
- Kolom **harga_grosir** dan **min_qty_grosir** lama masih berfungsi tapi **deprecated**
- Untuk produk baru, **gunakan sistem harga variasi** yang baru

### 📊 Contoh Kasus:

#### Kasus 1: Produk dengan 3 tier
```
Produk: Gula Pasir (1kg)
- Harga Normal: Rp 15.000
- Tier 1: 10+ kg = Rp 14.500/kg
- Tier 2: 50+ kg = Rp 14.000/kg
- Tier 3: 100+ kg = Rp 13.500/kg

Pembelian:
- Beli 5 kg  → 5 × Rp 15.000 = Rp 75.000
- Beli 10 kg → 10 × Rp 14.500 = Rp 145.000 ✅ (hemat Rp 5.000)
- Beli 50 kg → 50 × Rp 14.000 = Rp 700.000 ✅ (hemat Rp 50.000)
```

#### Kasus 2: Customer menambah quantity di kasir
```
1. Tambah 5 pcs → Total Rp 75.000 (@ Rp 15.000)
2. Tambah 5 pcs lagi → Total Rp 145.000 (@ Rp 14.500) ✅ otomatis ganti tier!
3. Kurangi jadi 8 pcs → Total Rp 120.000 (@ Rp 15.000) ✅ kembali ke normal
```

## Troubleshooting

### Harga tidak berubah otomatis di kasir?
- Clear browser cache dan refresh halaman
- Pastikan migration sudah dijalankan
- Cek apakah harga variasi sudah tersimpan di produk

### Data harga grosir lama tidak muncul?
- Jalankan ulang migration: `scripts\migrate_harga_variasi.bat`
- Data lama akan otomatis dimigrasi ke sistem baru

### Error "table harga_variasi not found"?
- Anda belum menjalankan migration
- Jalankan: `scripts\migrate_harga_variasi.bat`

## Database Schema

```sql
CREATE TABLE harga_variasi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produk_id INTEGER NOT NULL,
    min_qty INTEGER NOT NULL,
    harga REAL NOT NULL,
    keterangan VARCHAR(100),
    FOREIGN KEY (produk_id) REFERENCES produk(id) ON DELETE CASCADE
);
```

## API / Backend

### Model:
```python
class HargaVariasi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produk_id = db.Column(db.Integer, db.ForeignKey('produk.id'))
    min_qty = db.Column(db.Integer, nullable=False)
    harga = db.Column(db.Float, nullable=False)
    keterangan = db.Column(db.String(100))
```

### Method Helper di Produk:
```python
def get_harga_by_qty(self, qty):
    """Dapatkan harga berdasarkan quantity"""
    # Cari tier yang sesuai
    for variant in reversed(self.harga_variasi):
        if qty >= variant.min_qty:
            return variant.harga
    return self.harga_jual
```

---
**Update:** February 2026
**Version:** 2.0
