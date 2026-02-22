"""
Migration script untuk menambah kolom stok ke tabel VarianProduk
Jalankan dengan: python migrations/add_stok_varian.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.app_simple import app, db
from sqlalchemy import text

def migrate():
    """Add stok column to VarianProduk table"""
    with app.app_context():
        try:
            # Check if column sudah ada
            inspector = db.inspect(db.engine)
            columns = inspector.get_columns('varian_produk')

            column_names = [col['name'] for col in columns]
            if 'stok' in column_names:
                print("✓ Column 'stok' sudah ada di tabel 'varian_produk', skip migration")
                return True

            print("Adding column 'stok' to table 'varian_produk'...")

            # Add column menggunakan SQL raw karena alter table
            with db.engine.connect() as conn:
                # SQLite syntax untuk add column
                conn.execute(text("ALTER TABLE varian_produk ADD COLUMN stok INTEGER DEFAULT 0"))
                conn.commit()

            print("✓ Column 'stok' added successfully!")
            return True

        except Exception as e:
            print(f"✗ Error adding column: {str(e)}")
            return False

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)