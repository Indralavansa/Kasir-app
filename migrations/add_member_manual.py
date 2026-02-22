"""
Migrasi: Menambahkan kolom member_manual ke tabel transaksi
Untuk menyimpan input manual nama/telepon member
"""

import sys
import os

# Tambahkan path root project
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.app_simple import app, db

def migrate():
    with app.app_context():
        try:
            # Cek apakah kolom sudah ada
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('transaksi')]
            
            if 'member_manual' in columns:
                print("✓ Kolom member_manual sudah ada di tabel transaksi")
                return True
            
            # Tambahkan kolom member_manual
            print("Menambahkan kolom member_manual ke tabel transaksi...")
            from sqlalchemy import text
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE transaksi ADD COLUMN member_manual VARCHAR(100)'))
                conn.commit()
            
            print("✓ Kolom member_manual berhasil ditambahkan!")
            print("  Kolom ini digunakan untuk menyimpan input manual nama/telepon member")
            return True
            
        except Exception as e:
            print(f"✗ Error saat migrasi: {e}")
            return False

if __name__ == '__main__':
    print("="*60)
    print("MIGRASI: Menambahkan kolom member_manual")
    print("="*60)
    success = migrate()
    print("="*60)
    if success:
        print("MIGRASI BERHASIL!")
    else:
        print("MIGRASI GAGAL!")
    print("="*60)
