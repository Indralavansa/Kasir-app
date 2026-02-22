"""
Database Migration Script
Tambah tabel pengaturan untuk store settings
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = 'instance/kasir.db'

def migrate():
    """Create pengaturan table"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database tidak ditemukan: {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print(f"📅 Migration dimulai: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔗 Database: {DB_PATH}")
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pengaturan'")
        if cursor.fetchone():
            print("⚠️  Tabel pengaturan sudah ada")
            conn.close()
            return True
        
        # Create table
        print("➕ Membuat tabel pengaturan...")
        cursor.execute("""
            CREATE TABLE pengaturan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key VARCHAR(50) UNIQUE NOT NULL,
                value TEXT
            )
        """)
        
        # Insert default settings
        print("➕ Menambahkan pengaturan default...")
        default_settings = [
            ('store_name', 'TOKO SEMBAKO'),
            ('store_address', 'Jl. Contoh No. 123'),
            ('store_phone', '021-12345678'),
            ('receipt_footer', 'Terima kasih atas kunjungan Anda'),
            ('tax_enabled', 'false'),
            ('tax_percentage', '10')
        ]
        
        cursor.executemany("INSERT INTO pengaturan (key, value) VALUES (?, ?)", default_settings)
        
        conn.commit()
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM pengaturan")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"✅ Tabel pengaturan berhasil dibuat dengan {count} setting default")
            print(f"✓ Migration selesai: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            conn.close()
            return True
        else:
            print("❌ Gagal membuat tabel")
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
