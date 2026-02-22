@echo off
chcp 65001 > nul
echo ==========================================
echo   CLEANUP: Hapus Kolom Harga Grosir
echo ==========================================
echo.
echo PERINGATAN: Migration ini akan menghapus kolom deprecated
echo (harga_grosir dan min_qty_grosir) dari database.
echo.
echo Pastikan Anda sudah:
echo 1. Backup database
echo 2. Migrasi data ke harga_variasi
echo.

REM Change to parent directory (project root)
cd /d "%~dp0\.."

REM Check if venv exists
if not exist venv (
    echo Error: Virtual environment tidak ditemukan!
    echo Jalankan start_app.bat terlebih dahulu.
    pause
    exit /b 1
)

REM Activate venv and run migration
echo Menjalankan cleanup migration...
echo.
powershell -ExecutionPolicy Bypass -Command "& { . .\venv\Scripts\Activate.ps1; python migrations/remove_harga_grosir_columns.py }"

echo.
pause
