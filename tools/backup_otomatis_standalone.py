#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BACKUP OTOMATIS SYSTEM - STANDALONE VERSION
============================================
Script untuk backup produk, transaksi, dan database
Menggunakan SQLite3 (built-in Python, tanpa dependency ekstra)
"""

import os
import sys
import shutil
import csv
import json
import sqlite3
from datetime import datetime
from pathlib import Path

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ===============================
# CONFIG
# ===============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
DATA_DIR = os.path.join(BASE_DIR, 'data')
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
DB_PATH = os.path.join(INSTANCE_DIR, 'kasir.db')

# Pastikan direktori ada
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# ===============================
# COLORS FOR TERMINAL
# ===============================
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ===============================
# DATABASE CONNECTION
# ===============================
def get_db_connection():
    """Buat koneksi ke database SQLite"""
    if not os.path.exists(DB_PATH):
        print(f"{Colors.FAIL}❌ Database tidak ditemukan: {DB_PATH}{Colors.ENDC}")
        return None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"{Colors.FAIL}[ERROR] Gagal connect ke database: {str(e)}{Colors.ENDC}")
        return None

# ===============================
# BACKUP PRODUK
# ===============================
def backup_produk():
    """Backup semua data produk ke CSV dan JSON"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        conn = get_db_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        # Query produk dengan kategori
        cursor.execute("""
            SELECT 
                p.id, p.kode, p.nama, p.deskripsi,
                p.harga_beli, p.harga_jual, p.stok,
                COALESCE(k.nama, '-') as kategori,
                p.minimal_stok, p.satuan
            FROM produk p
            LEFT JOIN kategori k ON p.kategori_id = k.id
            ORDER BY p.id
        """)
        
        produk_list = cursor.fetchall()
        
        if not produk_list:
            print(f"{Colors.WARNING}[WARNING] Tidak ada produk untuk di-backup{Colors.ENDC}")
            conn.close()
            return
        
        # Backup ke CSV
        csv_filename = f"backup_produk_{timestamp}.csv"
        csv_path = os.path.join(DATA_DIR, csv_filename)
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['ID', 'Kode', 'Nama', 'Deskripsi', 'Harga Beli', 'Harga Jual', 
                         'Stok', 'Kategori', 'Minimal Stok', 'Satuan', 'Backup Date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for row in produk_list:
                writer.writerow({
                    'ID': row['id'],
                    'Kode': row['kode'],
                    'Nama': row['nama'],
                    'Deskripsi': row['deskripsi'] or '',
                    'Harga Beli': row['harga_beli'],
                    'Harga Jual': row['harga_jual'],
                    'Stok': row['stok'],
                    'Kategori': row['kategori'],
                    'Minimal Stok': row['minimal_stok'],
                    'Satuan': row['satuan'],
                    'Backup Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
        
        # Backup ke JSON
        json_filename = f"backup_produk_{timestamp}.json"
        json_path = os.path.join(DATA_DIR, json_filename)
        
        produk_data = []
        for row in produk_list:
            produk_data.append({
                'id': row['id'],
                'kode': row['kode'],
                'nama': row['nama'],
                'deskripsi': row['deskripsi'],
                'harga_beli': row['harga_beli'],
                'harga_jual': row['harga_jual'],
                'stok': row['stok'],
                'kategori': row['kategori'],
                'minimal_stok': row['minimal_stok'],
                'satuan': row['satuan']
            })
        
        with open(json_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(produk_data, jsonfile, ensure_ascii=False, indent=2)
        
        total = len(produk_list)
        print(f"{Colors.OKGREEN}[OK] Backup Produk Berhasil!{Colors.ENDC}")
        print(f"   📊 Total produk: {total}")
        print(f"   📄 CSV: {csv_filename}")
        print(f"   📋 JSON: {json_filename}")
        
        conn.close()
        
    except Exception as e:
        print(f"{Colors.FAIL}[ERROR] Gagal backup produk: {str(e)}{Colors.ENDC}")

# ===============================
# BACKUP TRANSAKSI
# ===============================
def backup_transaksi():
    """Backup semua data transaksi ke CSV dan JSON"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        conn = get_db_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        # Query transaksi dengan user dan member
        cursor.execute("""
            SELECT 
                t.id, t.kode_transaksi, t.tanggal,
                t.subtotal, t.discount_percent, t.discount_amount,
                t.total, t.bayar, t.kembalian, t.payment_method,
                COALESCE(u.nama, '-') as kasir,
                COALESCE(m.nama, t.member_manual, '-') as member,
                COALESCE(t.points_earned, 0) as points_earned
            FROM transaksi t
            LEFT JOIN user u ON t.user_id = u.id
            LEFT JOIN member m ON t.member_id = m.id
            ORDER BY t.tanggal DESC
        """)
        
        transaksi_list = cursor.fetchall()
        
        if not transaksi_list:
            print(f"{Colors.WARNING}[WARNING] Tidak ada transaksi untuk di-backup{Colors.ENDC}")
            conn.close()
            return
        
        # Backup ke CSV
        csv_filename = f"backup_transaksi_{timestamp}.csv"
        csv_path = os.path.join(DATA_DIR, csv_filename)
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['ID', 'Kode Transaksi', 'Tanggal', 'Subtotal', 'Diskon %', 'Diskon Rp',
                         'Total', 'Bayar', 'Kembalian', 'Metode Pembayaran', 'Kasir', 'Member',
                         'Poin Earned', 'Backup Date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for row in transaksi_list:
                writer.writerow({
                    'ID': row['id'],
                    'Kode Transaksi': row['kode_transaksi'],
                    'Tanggal': row['tanggal'],
                    'Subtotal': row['subtotal'],
                    'Diskon %': row['discount_percent'],
                    'Diskon Rp': row['discount_amount'],
                    'Total': row['total'],
                    'Bayar': row['bayar'],
                    'Kembalian': row['kembalian'],
                    'Metode Pembayaran': row['payment_method'].upper(),
                    'Kasir': row['kasir'],
                    'Member': row['member'],
                    'Poin Earned': row['points_earned'],
                    'Backup Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
        
        # Backup ke JSON
        json_filename = f"backup_transaksi_{timestamp}.json"
        json_path = os.path.join(DATA_DIR, json_filename)
        
        transaksi_data = []
        for row in transaksi_list:
            transaksi_data.append({
                'id': row['id'],
                'kode_transaksi': row['kode_transaksi'],
                'tanggal': row['tanggal'],
                'subtotal': row['subtotal'],
                'discount_percent': row['discount_percent'],
                'discount_amount': row['discount_amount'],
                'total': row['total'],
                'bayar': row['bayar'],
                'kembalian': row['kembalian'],
                'payment_method': row['payment_method'],
                'kasir': row['kasir'],
                'member': row['member'],
                'poin_earned': row['points_earned']
            })
        
        with open(json_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(transaksi_data, jsonfile, ensure_ascii=False, indent=2)
        
        total = len(transaksi_list)
        print(f"{Colors.OKGREEN}[OK] Backup Transaksi Berhasil!{Colors.ENDC}")
        print(f"   📊 Total transaksi: {total}")
        print(f"   📄 CSV: {csv_filename}")
        print(f"   📋 JSON: {json_filename}")
        
        conn.close()
        
    except Exception as e:
        print(f"{Colors.FAIL}[ERROR] Gagal backup transaksi: {str(e)}{Colors.ENDC}")

# ===============================
# BACKUP DATABASE LENGKAP
# ===============================
def backup_database():
    """Backup database lengkap"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"kasir_backup_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    
    try:
        if not os.path.exists(DB_PATH):
            print(f"{Colors.FAIL}❌ Database tidak ditemukan: {DB_PATH}{Colors.ENDC}")
            return
        
        shutil.copy2(DB_PATH, backup_path)
        filesize = os.path.getsize(backup_path) / (1024*1024)  # Convert to MB
        
        print(f"{Colors.OKGREEN}[OK] Backup Database Berhasil!{Colors.ENDC}")
        print(f"   📦 File: {backup_name}")
        print(f"   💾 Ukuran: {filesize:.2f} MB")
        
    except Exception as e:
        print(f"{Colors.FAIL}[ERROR] Gagal backup database: {str(e)}{Colors.ENDC}")

# ===============================
# BACKUP LENGKAP (SEMUA)
# ===============================
def backup_lengkap():
    """Backup semua (produk + transaksi + database)"""
    print(f"\n{Colors.BOLD}{Colors.OKBLUE}[AUTO] Memulai Backup Lengkap...{Colors.ENDC}\n")
    
    backup_produk()
    print()
    backup_transaksi()
    print()
    backup_database()
    
    print()
    cleanup_old_backups(keep=10)
    
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}[SUCCESS] Backup Lengkap Selesai!{Colors.ENDC}\n")

# ===============================
# LIST BACKUPS
# ===============================
def list_backups():
    """List semua file backup yang tersedia"""
    print(f"\n{Colors.BOLD}[BACKUP LIST]{Colors.ENDC}\n")
    
    # List database backups
    print(f"{Colors.OKBLUE}Database Backups:{Colors.ENDC}")
    db_files = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith('.db')], reverse=True)
    if db_files:
        for i, f in enumerate(db_files[:10], 1):
            path = os.path.join(BACKUP_DIR, f)
            size = os.path.getsize(path) / (1024*1024)
            print(f"  {i}. {f} ({size:.2f} MB)")
    else:
        print("  (Tidak ada)")
    
    # List produk backups
    print(f"\n{Colors.OKBLUE}Backup Produk:{Colors.ENDC}")
    produk_csv = sorted([f for f in os.listdir(DATA_DIR) if f.startswith('backup_produk_') and f.endswith('.csv')], reverse=True)
    if produk_csv:
        for i, f in enumerate(produk_csv[:5], 1):
            print(f"  {i}. {f}")
    else:
        print("  (Tidak ada)")
    
    # List transaksi backups
    print(f"\n{Colors.OKBLUE}Backup Transaksi:{Colors.ENDC}")
    transaksi_csv = sorted([f for f in os.listdir(DATA_DIR) if f.startswith('backup_transaksi_') and f.endswith('.csv')], reverse=True)
    if transaksi_csv:
        for i, f in enumerate(transaksi_csv[:5], 1):
            print(f"  {i}. {f}")
    else:
        print("  (Tidak ada)")
    
    print()

# ===============================
# CLEANUP OLD BACKUPS
# ===============================
def cleanup_old_backups(keep=10):
    """Hapus backup database lama, simpan N file terbaru"""
    try:
        db_files = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith('.db')], reverse=True)
        
        if len(db_files) <= keep:
            print(f"ℹ️ Database backup: {len(db_files)} file (simpan {keep})")
            return
        
        old_files = db_files[keep:]
        print(f"\n{Colors.WARNING}🗑️  Menghapus {len(old_files)} backup database lama...{Colors.ENDC}")
        
        for f in old_files:
            path = os.path.join(BACKUP_DIR, f)
            os.remove(path)
            print(f"   [-] Dihapus: {f}")
        
        print(f"{Colors.OKGREEN}[OK] Cleanup selesai. Mempertahankan {keep} backup terbaru.{Colors.ENDC}")
        
    except Exception as e:
        print(f"{Colors.FAIL}[ERROR] Gagal cleanup: {str(e)}{Colors.ENDC}")

# ===============================
# RESTORE DATABASE
# ===============================
def restore_database():
    """Restore database dari backup"""
    print(f"\n{Colors.BOLD}[RESTORE DATABASE]{Colors.ENDC}\n")
    
    db_backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith('.db')], reverse=True)
    
    if not db_backups:
        print(f"{Colors.WARNING}⚠️ Tidak ada backup untuk direstore{Colors.ENDC}")
        return
    
    print(f"Backup yang tersedia (5 terbaru):")
    for i, f in enumerate(db_backups[:5], 1):
        path = os.path.join(BACKUP_DIR, f)
        size = os.path.getsize(path) / (1024*1024)
        print(f"  {i}. {f} ({size:.2f} MB)")
    
    try:
        pilihan = input(f"\n{Colors.BOLD}Pilih nomor backup (default=1): {Colors.ENDC}").strip()
        pilihan = int(pilihan) if pilihan else 1
        
        if pilihan < 1 or pilihan > len(db_backups[:5]):
            print(f"{Colors.FAIL}❌ Pilihan tidak valid{Colors.ENDC}")
            return
        
        selected_backup = db_backups[pilihan-1]
        backup_path = os.path.join(BACKUP_DIR, selected_backup)
        
        # Konfirmasi
        confirm = input(f"\n{Colors.WARNING}⚠️ Yakin restore dari {selected_backup}? (y/n): {Colors.ENDC}").strip().lower()
        if confirm != 'y':
            print("Dibatalkan.")
            return
        
        # Create backup of current database first
        if os.path.exists(DB_PATH):
            backup_current = os.path.join(BACKUP_DIR, f"kasir_backup_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
            shutil.copy2(DB_PATH, backup_current)
            print(f"   💾 Backup database saat ini: kasir_backup_before_restore_*.db")
        
        # Restore
        shutil.copy2(backup_path, DB_PATH)
        print(f"{Colors.OKGREEN}[OK] Restore berhasil dari: {selected_backup}{Colors.ENDC}\n")
        
    except ValueError:
        print(f"{Colors.FAIL}[ERROR] Input tidak valid{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}[ERROR] Gagal restore: {str(e)}{Colors.ENDC}")

# ===============================
# MAIN MENU
# ===============================
def show_menu():
    """Tampilkan menu interaktif"""
    print(f"\n{Colors.BOLD}{Colors.OKBLUE}{'='*60}")
    print("[BACKUP] SISTEM BACKUP OTOMATIS - TOKO SEMBAKO KASIR")
    print(f"{'='*60}{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}Pilih opsi:{Colors.ENDC}")
    print("1. Backup Produk (CSV + JSON)")
    print("2. Backup Transaksi (CSV + JSON)")
    print("3. Backup Database Lengkap (SQLite)")
    print("4. Backup Semua (Produk + Transaksi + Database)")
    print("5. List Semua Backup")
    print("6. Restore Database dari Backup")
    print("7. Cleanup Backup Lama")
    print("0. Keluar")
    print()
    
    pilihan = input(f"{Colors.BOLD}Pilihan (0-7): {Colors.ENDC}").strip()
    
    return pilihan

def main_interactive():
    """Main loop interaktif"""
    while True:
        try:
            pilihan = show_menu()
            
            if pilihan == '1':
                backup_produk()
            elif pilihan == '2':
                backup_transaksi()
            elif pilihan == '3':
                backup_database()
            elif pilihan == '4':
                backup_lengkap()
            elif pilihan == '5':
                list_backups()
            elif pilihan == '6':
                restore_database()
            elif pilihan == '7':
                cleanup_old_backups()
            elif pilihan == '0':
                print(f"\n{Colors.OKGREEN}Terima kasih! Sampai jumpa.{Colors.ENDC}\n")
                break
            else:
                print(f"{Colors.FAIL}❌ Pilihan tidak valid{Colors.ENDC}")
                
            input(f"\n{Colors.BOLD}Press Enter untuk melanjutkan...{Colors.ENDC}")
            
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}Dibatalkan oleh user{Colors.ENDC}")
            break
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {str(e)}{Colors.ENDC}")

# ===============================
# COMMAND LINE ARGUMENTS
# ===============================
def main():
    """Main function dengan CLI support"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'auto':
            # Auto backup semua
            backup_lengkap()
        elif command == 'produk':
            backup_produk()
        elif command == 'transaksi':
            backup_transaksi()
        elif command == 'database':
            backup_database()
        elif command == 'list':
            list_backups()
        elif command == 'cleanup':
            cleanup_old_backups()
        elif command == '--help' or command == '-h':
            print(f"""
{Colors.BOLD}BACKUP OTOMATIS - USAGE{Colors.ENDC}

Usage: python backup_otomatis.py [command]

Commands:
  (no args)     - Interactive menu
  auto          - Auto backup semua (produk + transaksi + database)
  produk        - Backup hanya produk
  transaksi     - Backup hanya transaksi
  database      - Backup hanya database
  list          - List semua backup files
  cleanup       - Hapus backup lama
  --help        - Tampilkan help

Contoh:
  python backup_otomatis.py auto
  python backup_otomatis.py produk
  python backup_otomatis.py list
            """)
        else:
            print(f"{Colors.FAIL}[ERROR] Unknown command: {command}{Colors.ENDC}")
            print("Use --help for more information")
    else:
        # Interactive menu
        main_interactive()

if __name__ == '__main__':
    main()
