"""
Database Migration Script
Tambah kolom payment_method ke tabel transaksi
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = 'instance/kasir.db'

def migrate():
    """Add payment_method column to transaksi table"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database tidak ditemukan: {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print(f"📅 Migration dimulai: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔗 Database: {DB_PATH}")
        
        # Check apakah kolom sudah ada
        cursor.execute("PRAGMA table_info(transaksi)")
        columns = {col[1] for col in cursor.fetchall()}
        
        if 'payment_method' in columns:
            print("⚠️  Kolom payment_method sudah ada, skip migration")
            conn.close()
            return True
        
        # Add kolom
        print("➕ Menambahkan kolom payment_method ke tabel transaksi...")
        cursor.execute("""
            ALTER TABLE transaksi 
            ADD COLUMN payment_method VARCHAR(20) DEFAULT 'tunai'
        """)
        
        conn.commit()
        
        # Verify
        cursor.execute("PRAGMA table_info(transaksi)")
        columns = {col[1] for col in cursor.fetchall()}
        
        if 'payment_method' in columns:
            print("✅ Kolom payment_method berhasil ditambahkan")
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
