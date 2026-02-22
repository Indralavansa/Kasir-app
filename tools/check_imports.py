import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.app_simple import db, app, Produk

with app.app_context():
    products = Produk.query.limit(10).all()
    print(f"Total produk: {Produk.query.count()}\n")
    print("10 Produk pertama:")
    for i, p in enumerate(products, 1):
        print(f"{i}. Kode: {p.kode:25} | Nama: {p.nama:30} | Satuan: {p.satuan:8} | Harga: Rp {p.harga_jual:,.0f}")
