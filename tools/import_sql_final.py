#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script untuk import produk dari SQL file dengan parsing yang lebih baik
Menggunakan regex dan proper CSV parsing
"""

import sys
import os
import re
import csv
from pathlib import Path
from io import StringIO

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.app_simple import db, app, Produk

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_MDB_PATH = BASE_DIR / "data" / "dbamiramart_2026February - Copy (2).MDB"
MDB_FILE = os.environ.get("MDB_PATH", str(DEFAULT_MDB_PATH))

def extract_sql_rows():
    """Extract semua VALUES rows dari SQL file"""
    with open(MDB_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find VALUES clause
    match = re.search(r'VALUES\s+(.*?)(?:;|$)', content, re.DOTALL | re.IGNORECASE)
    if not match:
        return []
    
    values_str = match.group(1)
    
    # Split row strings properly
    rows = []
    depth = 0
    in_string = False
    current_row = []
    
    for i, char in enumerate(values_str):
        # Track string boundaries
        if char == "'" and (i == 0 or values_str[i-1] != '\\'):
            in_string = not in_string
        
        # Track parentheses
        if char == '(' and not in_string:
            depth += 1
            if depth == 1:
                current_row = []
                continue
        elif char == ')' and not in_string:
            depth -= 1
            if depth == 0 and current_row:
                rows.append(''.join(current_row))
        
        if depth > 0:
            current_row.append(char)
    
    return rows

def parse_csv_row(row_str):
    """Parse row string as CSV"""
    # Use Python's CSV module for proper parsing
    try:
        reader = csv.reader(StringIO(row_str))
        values = next(reader)
        return values
    except:
        # Fallback: simple split by comma respecting quotes
        values = []
        current = []
        in_string = False
        
        for char in row_str:
            if char == "'" and (not current or current[-1] != '\\'):
                in_string = not in_string
            elif char == ',' and not in_string:
                val = ''.join(current).strip()
                # Remove quotes if present
                if val.startswith("'") and val.endswith("'"):
                    val = val[1:-1]
                values.append(val)
                current = []
                continue
            
            current.append(char)
        
        if current:
            val = ''.join(current).strip()
            if val.startswith("'") and val.endswith("'"):
                val = val[1:-1]
            values.append(val)
        
        return values

def migrate_with_better_parsing():
    """Import dengan parsing yang lebih baik"""
    
    print("=" * 70)
    print("IMPORT PRODUK DARI SQL (IMPROVED PARSING)")
    print("=" * 70)
    
    print(f"\n📂 Membaca file SQL: {MDB_FILE}")
    
    try:
        # Extract rows
        print("\n🔍 Extracting rows dari SQL...")
        rows = extract_sql_rows()
        print(f"✅ Ditemukan {len(rows)} rows")
        
        # Parse to products
        products = []
        print(f"\n📦 Parsing data...")
        
        for idx, row_str in enumerate(rows):
            try:
                values = parse_csv_row(row_str)
                
                if len(values) < 41:
                    continue
                
                # Column mapping
                # 2: kodeitem (numeric)
                # 3: barcode (string/empty)
                # 4: item (product name)
                # 11: satuan
                # 20: hargabeli
                # 40: hargajual1
                
                kode = values[3].strip() if len(values) > 3 else ''  # barcode
                if not kode or kode.upper() == 'NULL':
                    # Try kodeitem as fallback
                    kode_2 = values[2].strip() if len(values) > 2 else ''
                    if kode_2 and kode_2.upper() != 'NULL':
                        kode = kode_2
                
                nama = values[4].strip() if len(values) > 4 else 'Unknown'
                satuan = values[11].strip() if len(values) > 11 else 'pcs'
                
                if not satuan or satuan.upper() == 'NULL':
                    satuan = 'pcs'
                
                try:
                    harga_beli = float(values[20] or 0) if len(values) > 20 else 0
                except:
                    harga_beli = 0
                
                try:
                    harga_jual = float(values[40] or 0) if len(values) > 40 else 0
                except:
                    harga_jual = 0
                
                # Skip invalid
                if not kode or kode.upper() == 'NULL' or not nama:
                    continue
                
                products.append({
                    'kode': kode,
                    'nama': nama,
                    'satuan': satuan,
                    'harga_beli': harga_beli,
                    'harga_jual': harga_jual
                })
                
                if (idx + 1) % 100 == 0:
                    print(f"   ✅ Processed {idx + 1}...")
            
            except Exception as e:
                pass
        
        print(f"\n✅ Total products parsed: {len(products)}")
        
        if products:
            print(f"\n📦 Preview (5 products):")
            for i, p in enumerate(products[:5], 1):
                print(f"   {i}. {p['kode']:20} | {p['nama'][:30]:30} | {p['satuan']:8} | Rp {p['harga_jual']:,.0f}")
        
        # Import ke DB
        print(f"\n🔄 Importing ke database...")
        
        with app.app_context():
            imported = 0
            duplicate = 0
            
            for prod in products:
                try:
                    if Produk.query.filter_by(kode=prod['kode']).first():
                        duplicate += 1
                        continue
                    
                    produk = Produk(
                        kode=prod['kode'],
                        nama=prod['nama'],
                        satuan=prod['satuan'],
                        harga_beli=prod['harga_beli'],
                        harga_jual=prod['harga_jual'],
                        stok=0,
                        minimal_stok=0
                    )
                    db.session.add(produk)
                    imported += 1
                    
                    if (imported + duplicate) % 50 == 0:
                        print(f"   ✅ Imported {imported}...")
                
                except Exception as e:
                    print(f"   ❌ Error: {e}")
            
            db.session.commit()
            print(f"\n" + "=" * 70)
            print(f"✅ IMPORT COMPLETED!")
            print(f"   - Produk imported: {imported}")
            print(f"   - Duplicates: {duplicate}")
            print(f"   - Total: {len(products)}")
            print(f"   - Total in DB: {Produk.query.count()}")
            print("=" * 70)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    migrate_with_better_parsing()
