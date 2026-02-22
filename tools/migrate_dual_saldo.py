#!/usr/bin/env python3
"""
Migrasi database untuk sistem dual-saldo
Menambahkan kolom-kolom baru ke existing database
"""
import sqlite3
import os
import sys
from datetime import datetime

DB_PATH = "instance/kasir.db"

def column_exists(conn, table, column):
    """Check if column exists in table"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    return column in columns

def migrate():
    """Run migration"""
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("MIGRATION: Dual Saldo System")
        print("=" * 60)
        
        # 1. Add sumber_saldo to KasMutasi
        if not column_exists(conn, 'kas_mutasi', 'sumber_saldo'):
            print("\n1. Adding 'sumber_saldo' column to kas_mutasi...")
            cursor.execute("""
                ALTER TABLE kas_mutasi 
                ADD COLUMN sumber_saldo VARCHAR(20) DEFAULT 'harian'
            """)
            print("   ✓ Column added")
        else:
            print("\n1. 'sumber_saldo' already exists in kas_mutasi")
        
        # 2. Add saldo_harian_input to DailySaldoArchive
        if not column_exists(conn, 'daily_saldo_archive', 'saldo_harian_input'):
            print("\n2. Adding 'saldo_harian_input' column to daily_saldo_archive...")
            cursor.execute("""
                ALTER TABLE daily_saldo_archive 
                ADD COLUMN saldo_harian_input FLOAT DEFAULT 0
            """)
            print("   ✓ Column added")
        else:
            print("\n2. 'saldo_harian_input' already exists in daily_saldo_archive")
        
        # 3. Check if Pengaturan table exists, if not create it
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='pengaturan'
        """)
        if cursor.fetchone():
            print("\n3. Pengaturan table already exists")
        else:
            print("\n3. Creating Pengaturan table...")
            cursor.execute("""
                CREATE TABLE pengaturan (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key VARCHAR(50) UNIQUE NOT NULL,
                    value TEXT
                )
            """)
            print("   ✓ Table created")
        
        # 4. Initialize saldo_harian_hari_ini setting
        cursor.execute("""
            SELECT value FROM pengaturan 
            WHERE key='saldo_harian_hari_ini'
        """)
        if cursor.fetchone():
            print("\n4. saldo_harian_hari_ini setting already exists")
        else:
            print("\n4. Initializing saldo_harian_hari_ini setting...")
            cursor.execute("""
                INSERT INTO pengaturan (key, value) 
                VALUES ('saldo_harian_hari_ini', '0')
            """)
            print("   ✓ Setting initialized to 0")
        
        conn.commit()
        print("\n" + "=" * 60)
        print("✅ MIGRATION SUCCESSFUL")
        print("=" * 60)
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ MIGRATION FAILED: {e}")
        return False

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)
