"""
Migration script untuk menambah kolom varian_barcode dan varian_nama ke tabel TransaksiItem
Jalankan dengan: python migrations/add_varian_transaksi.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.app_simple import app, db
from sqlalchemy import text

def migrate():
    """Add varian_barcode and varian_nama columns to TransaksiItem table"""
    with app.app_context():
        try:
            # Check if columns sudah ada
            inspector = db.inspect(db.engine)
            columns = inspector.get_columns('transaksi_item')

            column_names = [col['name'] for col in columns]
            if 'varian_barcode' in column_names and 'varian_nama' in column_names:
                print("✓ Columns 'varian_barcode' and 'varian_nama' sudah ada di tabel 'transaksi_item', skip migration")
                return True

            print("Adding columns 'varian_barcode' and 'varian_nama' to table 'transaksi_item'...")

            # Add columns menggunakan SQL raw karena alter table
            with db.engine.connect() as conn:
                # SQLite syntax untuk add columns
                if 'varian_barcode' not in column_names:
                    conn.execute(text("ALTER TABLE transaksi_item ADD COLUMN varian_barcode VARCHAR(100)"))
                if 'varian_nama' not in column_names:
                    conn.execute(text("ALTER TABLE transaksi_item ADD COLUMN varian_nama VARCHAR(200)"))
                conn.commit()

            print("✓ Columns 'varian_barcode' and 'varian_nama' added successfully!")
            return True

        except Exception as e:
            print(f"✗ Error adding columns: {str(e)}")
            return False

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)