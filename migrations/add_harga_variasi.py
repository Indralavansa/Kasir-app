"""
Migration: Menambahkan tabel HargaVariasi untuk sistem harga bertingkat
Run this script to add the new price variants table to existing database
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from app.app_simple import db, app

def migrate():
    """Run migration to add HargaVariasi table"""
    
    print("=" * 60)
    print("MIGRATION: Menambahkan Tabel HargaVariasi")
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
        
        # Check if table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='harga_variasi'
        """)
        
        if cursor.fetchone():
            print("⚠️  Table 'harga_variasi' sudah ada, skip migration")
            conn.close()
            return True
        
        # Create HargaVariasi table
        print("\n[1/3] Membuat tabel harga_variasi...")
        cursor.execute("""
            CREATE TABLE harga_variasi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produk_id INTEGER NOT NULL,
                min_qty INTEGER NOT NULL,
                harga REAL NOT NULL,
                keterangan VARCHAR(100),
                FOREIGN KEY (produk_id) REFERENCES produk(id) ON DELETE CASCADE
            )
        """)
        
        print("✓ Tabel harga_variasi berhasil dibuat")
        
        # Migrate existing harga_grosir to harga_variasi
        print("\n[2/3] Migrasi data harga grosir lama ke harga variasi...")
        cursor.execute("""
            SELECT id, harga_grosir, min_qty_grosir 
            FROM produk 
            WHERE harga_grosir IS NOT NULL AND harga_grosir > 0
        """)
        
        old_grosir = cursor.fetchall()
        migrated = 0
        
        for produk_id, harga_grosir, min_qty_grosir in old_grosir:
            cursor.execute("""
                INSERT INTO harga_variasi (produk_id, min_qty, harga, keterangan)
                VALUES (?, ?, ?, ?)
            """, (produk_id, min_qty_grosir or 10, harga_grosir, 'Grosir'))
            migrated += 1
        
        print(f"✓ Migrasi {migrated} harga grosir ke harga variasi")
        
        # Create index for better performance
        print("\n[3/3] Membuat index untuk performa...")
        cursor.execute("""
            CREATE INDEX idx_harga_variasi_produk 
            ON harga_variasi(produk_id)
        """)
        
        cursor.execute("""
            CREATE INDEX idx_harga_variasi_min_qty 
            ON harga_variasi(produk_id, min_qty)
        """)
        
        print("✓ Index berhasil dibuat")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ MIGRATION BERHASIL!")
        print("=" * 60)
        print("\nCatatan:")
        print("- Tabel harga_variasi sudah ditambahkan")
        print("- Data harga grosir lama sudah dimigrasi")
        print("- Kolom harga_grosir dan min_qty_grosir masih ada (deprecated)")
        print("- Gunakan form produk untuk mengelola harga variasi baru")
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
