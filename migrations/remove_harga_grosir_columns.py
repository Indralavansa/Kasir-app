"""
Migration: Menghapus kolom harga_grosir dan min_qty_grosir dari tabel produk
Run this script to clean up deprecated columns (OPTIONAL)
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3

def migrate():
    """Run migration to remove deprecated columns"""
    
    print("=" * 60)
    print("MIGRATION: Menghapus Kolom Harga Grosir (Deprecated)")
    print("=" * 60)
    
    # Get database path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'instance', 'kasir.db')
    
    if not os.path.exists(db_path):
        print(f"✗ Database tidak ditemukan: {db_path}")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n⚠️  PERINGATAN:")
        print("Migration ini akan menghapus kolom harga_grosir dan min_qty_grosir")
        print("dari tabel produk. Data akan hilang permanen!")
        print("\nPastikan Anda sudah:")
        print("1. Backup database")
        print("2. Migrasi data harga grosir ke harga_variasi")
        print("")
        
        response = input("Lanjutkan? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("\n✗ Migration dibatalkan")
            conn.close()
            return False
        
        # Check if columns exist
        cursor.execute("PRAGMA table_info(produk)")
        columns = [col[1] for col in cursor.fetchall()]
        
        has_harga_grosir = 'harga_grosir' in columns
        has_min_qty_grosir = 'min_qty_grosir' in columns
        
        if not has_harga_grosir and not has_min_qty_grosir:
            print("\n⚠️  Kolom sudah tidak ada, skip migration")
            conn.close()
            return True
        
        print("\n[1/2] Membuat tabel produk baru tanpa kolom deprecated...")
        
        # Create new table without deprecated columns
        cursor.execute("""
            CREATE TABLE produk_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kode VARCHAR(50) UNIQUE NOT NULL,
                nama VARCHAR(200) NOT NULL,
                deskripsi TEXT,
                harga_beli REAL NOT NULL,
                harga_jual REAL NOT NULL,
                stok INTEGER DEFAULT 0,
                kategori_id INTEGER,
                minimal_stok INTEGER DEFAULT 5,
                satuan VARCHAR(20) DEFAULT 'pcs',
                FOREIGN KEY (kategori_id) REFERENCES kategori(id)
            )
        """)
        
        print("✓ Tabel baru berhasil dibuat")
        
        print("\n[2/2] Copy data dari tabel lama ke tabel baru...")
        
        # Copy data
        cursor.execute("""
            INSERT INTO produk_new (id, kode, nama, deskripsi, harga_beli, harga_jual, 
                                   stok, kategori_id, minimal_stok, satuan)
            SELECT id, kode, nama, deskripsi, harga_beli, harga_jual, 
                   stok, kategori_id, minimal_stok, satuan
            FROM produk
        """)
        
        rows_copied = cursor.rowcount
        print(f"✓ {rows_copied} produk berhasil di-copy")
        
        # Drop old table
        cursor.execute("DROP TABLE produk")
        
        # Rename new table
        cursor.execute("ALTER TABLE produk_new RENAME TO produk")
        
        print("✓ Tabel lama dihapus, tabel baru di-rename")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ MIGRATION BERHASIL!")
        print("=" * 60)
        print("\nKolom yang dihapus:")
        print("- harga_grosir")
        print("- min_qty_grosir")
        print("\nSekarang hanya menggunakan sistem harga_variasi")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: Migration gagal!")
        print(f"Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)
