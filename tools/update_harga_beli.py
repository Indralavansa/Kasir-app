#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update harga_beli dari file database (menggunakan hpp column)
"""

import sys
import os
import re
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.app_simple import db, app, Produk

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_MDB_PATH = BASE_DIR / "data" / "dbamiramart_2026February - Copy (2).MDB"
MDB_FILE = os.environ.get("MDB_PATH", str(DEFAULT_MDB_PATH))

def extract_values_from_tuple(tuple_str):
    """Extract individual values dari tuple"""
    tuple_str = tuple_str.strip()
    if tuple_str.startswith('('):
        tuple_str = tuple_str[1:]
    if tuple_str.endswith(')'):
        tuple_str = tuple_str[:-1]
    
    values = []
    parts = []
    current = ""
    in_quote = False
    prev_char = ""
    
    for char in tuple_str:
        if char == "'" and prev_char != "\\":
            in_quote = not in_quote
            current += char
        elif char == "," and not in_quote:
            parts.append(current.strip())
            current = ""
        else:
            current += char
        prev_char = char
    
    if current:
        parts.append(current.strip())
    
    # Parse each part
    for part in parts:
        if part.upper() == "NULL":
            values.append(None)
        elif part.startswith("'") and part.endswith("'"):
            # Remove quotes and unescape
            val = part[1:-1].replace("''", "'")
            values.append(val)
        else:
            try:
                values.append(float(part))
            except:
                values.append(part)
    
    return values

def parse_sql_values(content):
    """Parse SQL VALUES dari file dengan regex"""
    match = re.search(r'VALUES\s*\((.*)\);', content, re.DOTALL)
    if not match:
        print("❌ VALUES clause tidak ditemukan")
        return []
    
    values_content = match.group(1)
    tuples = re.findall(r'\([^)]*(?:(?:\([^)]*\)[^)]*)*[^)]*)\)', values_content)
    
    return tuples

def main():
    print("📖 Reading SQL file...")
    try:
        with open(MDB_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    print(f"📊 File size: {len(content)} characters")
    
    # Parse VALUES
    tuples = parse_sql_values(content)
    
    if not tuples:
        print("❌ Tidak ada data ditemukan")
        return
    
    print(f"✅ Ditemukan {len(tuples)} tuples")
    
    # Mapping dari file:
    # Index 3: barcode
    # Index 4: item (nama)
    # Index 20: hargabeli
    # Index 22: hpp (harga pokok penjualan)
    
    print("\n💾 Updating harga_beli dari kolom hpp...")
    
    with app.app_context():
        updated = 0
        failed = 0
        
        for i, tuple_str in enumerate(tuples):
            try:
                values = extract_values_from_tuple(tuple_str)
                
                if len(values) < 23:
                    failed += 1
                    continue
                
                # Extract values
                barcode = str(values[3]) if values[3] else None
                nama = str(values[4]) if values[4] else None
                hpp = float(values[22]) if isinstance(values[22], (int, float)) and values[22] else 0
                
                if not barcode:
                    failed += 1
                    continue
                
                # Find dan update produk
                produk = Produk.query.filter_by(kode=barcode).first()
                if produk:
                    old_harga = produk.harga_beli
                    produk.harga_beli = hpp
                    updated += 1
                    
                    if (i + 1) % 50 == 0:
                        print(f"  ✅ Updated {i + 1}/{len(tuples)}")
                else:
                    # Produk tidak ada di database
                    failed += 1
                
            except Exception as e:
                print(f"  ❌ Tuple {i+1}: {str(e)[:60]}")
                failed += 1
        
        # Commit
        try:
            db.session.commit()
            print(f"\n✅ SUCCESS!")
            print(f"   - Updated: {updated}")
            print(f"   - Failed: {failed}")
            
            # Sample verification
            print(f"\n📊 Sample Updated Products:")
            for p in Produk.query.limit(5).all():
                print(f"   {p.kode} | {p.nama[:30]:30} | Beli: Rp {p.harga_beli:>10,.0f} | Jual: Rp {p.harga_jual:>10,.0f}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Commit failed: {e}")

if __name__ == '__main__':
    main()
