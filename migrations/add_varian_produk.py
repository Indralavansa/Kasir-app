"""
Migration script untuk menambah tabel VarianProduk
Jalankan dengan: python migrations/add_varian_produk.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.app_simple import app, db, VarianProduk, Produk
from datetime import datetime

def migrate():
    """Create VarianProduk table jika belum ada"""
    with app.app_context():
        try:
            # Check if table sudah ada
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'varian_produk' in tables:
                print("✓ Table 'varian_produk' sudah ada, skip creation")
                return True
            
            print("Creating table 'varian_produk'...")
            db.create_all()
            print("✓ Table 'varian_produk' created successfully!")
            
            return True
        except Exception as e:
            print(f"✗ Error creating table: {str(e)}")
            return False

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)
