"""
Database Migration Script
Tambah kolom harga_grosir dan min_qty_grosir ke tabel produk
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = 'instance/kasir.db'

def migrate():
    """Add price variant columns to produk table"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database tidak ditemukan: {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print(f"📅 Migration dimulai: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔗 Database: {DB_PATH}")
        
        # Check kolom yang sudah ada
        cursor.execute("PRAGMA table_info(produk)")
        columns = {col[1] for col in cursor.fetchall()}
        
        changes_made = False
        
        # Add harga_grosir
        if 'harga_grosir' not in columns:
            print("➕ Menambahkan kolom harga_grosir...")
            cursor.execute("""
                ALTER TABLE produk 
                ADD COLUMN harga_grosir FLOAT
            """)
            changes_made = True
        else:
            print("⚠️  Kolom harga_grosir sudah ada")
        
        # Add min_qty_grosir
        if 'min_qty_grosir' not in columns:
            print("➕ Menambahkan kolom min_qty_grosir...")
            cursor.execute("""
                ALTER TABLE produk 
                ADD COLUMN min_qty_grosir INTEGER DEFAULT 10
            """)
            changes_made = True
        else:
            print("⚠️  Kolom min_qty_grosir sudah ada")
        
        if changes_made:
            conn.commit()
            print("✅ Migration berhasil!")
        else:
            print("ℹ️  Tidak ada perubahan, semua kolom sudah ada")
        
        # Verify
        cursor.execute("PRAGMA table_info(produk)")
        columns = {col[1] for col in cursor.fetchall()}
        
        if 'harga_grosir' in columns and 'min_qty_grosir' in columns:
            print(f"✓ Kolom harga_grosir dan min_qty_grosir tersedia")
            print(f"✓ Migration selesai: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            conn.close()
            return True
        else:
            print("❌ Gagal menambahkan kolom")
            conn.close()
            return False
            
    except sqlite3.Error as e:
        print(f"❌ Database Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    success = migrate()
    exit(0 if success else 1)
