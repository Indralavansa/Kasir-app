#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script untuk extract MDB ke CSV menggunakan PowerShell dan COM
"""

import sys
import os
import subprocess
import json
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.app_simple import db, app, Produk

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_MDB_PATH = BASE_DIR / "data" / "dbamiramart_2026February - Copy (2).MDB"
MDB_PATH = os.environ.get("MDB_PATH", str(DEFAULT_MDB_PATH))

def extract_mdb_to_csv():
    """Extract tabel produk dari MDB ke CSV menggunakan COM object"""
    
    print("=" * 70)
    print("EXTRACT MDB KE CSV (Menggunakan COM)")
    print("=" * 70)
    
    csv_output = str(BASE_DIR / "data" / "produk_mdb_temp.csv")
    
    # PowerShell script untuk extract MDB ke CSV
    ps_script = f"""
$mdbPath = '{MDB_PATH}'
$csvPath = '{csv_output}'

try {{
    # Create COM object untuk Access
    $acl = New-Object -ComObject 'Access.Application'
    $acl.Visible = $False
    
    # Buka database
    $db = $acl.OpenCurrentDatabase($mdbPath)
    
    # Get tabel produk
    $tbl = $db.TableDefs('produk')
    
    # Export ke CSV (menggunakan DoCmd)
    # Access DAO bagian dari ADODB
    [System.Reflection.Assembly]::LoadWithoutException('stdole.dll') | Out-Null
    
    # Alternatif: gunakan ADODB untuk export
    $conn = New-Object -ComObject 'ADODB.Connection'
    $provider = 'Microsoft.JET.OLEDB.4.0'
    
    $conn.Open("Provider=$provider;Data Source=$mdbPath;")
    
    # Baca data dari tabel
    $rs = New-Object -ComObject 'ADODB.Recordset'
    $rs.Open('SELECT * FROM produk', $conn)
    
    # Export ke CSV
    $rs.Save($csvPath, 1)  # adPersistCSV = 1
    
    $rs.Close()
    $conn.Close()
    
    Write-Host "✅ Berhasil export ke CSV: $csvPath"
}}
catch {{
    Write-Host "❌ Error: $_"
    exit 1
}}
"""
    
    # Write PS script ke temporary file
    ps_file = str(BASE_DIR / "data" / "extract_mdb_temp.ps1")
    with open(ps_file, 'w', encoding='utf-8') as f:
        f.write(ps_script)
    
    print(f"\n🔧 Menjalankan PowerShell untuk extract MDB...")
    
    try:
        # Jalankan PowerShell
        result = subprocess.run(
            ['powershell', '-ExecutionPolicy', 'Bypass', '-File', ps_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if result.returncode == 0 and os.path.exists(csv_output):
            print(f"\n✅ File CSV berhasil dibuat: {csv_output}")
            return csv_output
        else:
            print(f"⚠️  Export gagal, coba metode alternatif...")
            return None
    
    except Exception as e:
        print(f"❌ Error menjalankan PowerShell: {e}")
        return None
    finally:
        # Cleanup PS file
        if os.path.exists(ps_file):
            os.remove(ps_file)

def import_csv_to_db(csv_file):
    """Import CSV ke SQLite"""
    
    if not os.path.exists(csv_file):
        print(f"❌ File CSV tidak ditemukan: {csv_file}")
        return
    
    print(f"\n📂 Membaca file CSV: {csv_file}")
    
    import csv
    
    try:
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        print(f"✅ Ditemukan {len(rows)} baris")
        
        if rows:
            print(f"📋 Kolom: {list(rows[0].keys())}")
            print(f"\n📦 Data (3 baris pertama):")
            for i, row in enumerate(rows[:3], 1):
                print(f"   {i}. {row}")
        
        # Import ke database
        print(f"\n🔄 Mengimport ke database SQLite...")
        
        with app.app_context():
            imported = 0
            duplicate = 0
            error = 0
            
            for idx, row in enumerate(rows):
                try:
                    # Mapping case-insensitive
                    row_lower = {k.lower() if k else '': v for k, v in row.items()}
                    
                    kode = str(row_lower.get('barcode', '') or '').strip()
                    nama = str(row_lower.get('item', '') or '').strip()
                    satuan = str(row_lower.get('satuan', 'pcs') or 'pcs').strip()
                    
                    try:
                        harga_beli = float(str(row_lower.get('harga_beli', 0) or 0).replace(',', ''))
                    except:
                        harga_beli = 0
                    
                    try:
                        harga_jual = float(str(row_lower.get('harga_jual', 0) or 0).replace(',', ''))
                    except:
                        harga_jual = 0
                    
                    # Validasi
                    if not kode:
                        continue
                    
                    # Check duplikat
                    if Produk.query.filter_by(kode=kode).first():
                        duplicate += 1
                        continue
                    
                    # Insert
                    produk = Produk(
                        kode=kode, nama=nama, satuan=satuan,
                        harga_beli=harga_beli, harga_jual=harga_jual,
                        stok=0, minimal_stok=0
                    )
                    db.session.add(produk)
                    imported += 1
                    
                    if (idx + 1) % 20 == 0:
                        print(f"   ✅ Diproses {idx + 1}...")
                
                except Exception as e:
                    error += 1
                    print(f"   ❌ Baris {idx}: {e}")
            
            db.session.commit()
            print(f"\n" + "=" * 70)
            print(f"✅ IMPORT SELESAI!")
            print(f"   - Produk diimport: {imported}")
            print(f"   - Duplikat (skip): {duplicate}")
            print(f"   - Error: {error}")
            print(f"   - Total diproses: {len(rows)}")
            print("=" * 70)
    
    except Exception as e:
        print(f"❌ Error membaca CSV: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        if os.path.exists(csv_file):
            os.remove(csv_file)

def main():
    # Step 1: Extract MDB ke CSV
    csv_file = extract_mdb_to_csv()
    
    if csv_file:
        # Step 2: Import CSV ke database
        import_csv_to_db(csv_file)
    else:
        print("\n❌ Tidak bisa extract MDB ke CSV")
        print("   Pastikan Microsoft Access atau LibreOffice terinstall")

if __name__ == '__main__':
    main()
