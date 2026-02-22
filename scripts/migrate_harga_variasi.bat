@echo off
chcp 65001 > nul
echo ==========================================
echo   MIGRATION: Menambahkan Harga Variasi
echo ==========================================
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
echo Menjalankan migration...
echo.
powershell -ExecutionPolicy Bypass -Command "& { . .\venv\Scripts\Activate.ps1; python migrations/add_harga_variasi.py }"

echo.
pause
