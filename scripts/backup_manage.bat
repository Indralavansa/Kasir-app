@echo off
chcp 65001 > nul
title Backup Manager - Kasir Toko

REM ===============================
REM SET WORKING DIRECTORY
REM ===============================
cd /d "%~dp0\.."

REM ===============================
REM CHECK PYTHON
REM ===============================
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python tidak ditemukan di PATH
    echo Pastikan Python sudah terinstall dan ditambahkan ke PATH
    pause
    exit
)

REM ===============================
REM MENU
REM ===============================
:MENU
cls
echo ==========================================
echo   KASIR TOKO SEMBAKO - BACKUP MANAGEMENT
echo ==========================================
echo.
echo [1] List semua backup
echo [2] Restore backup TERBARU
echo [3] Backup manual sekarang
echo [4] Hapus backup lama (simpan 5 terbaru)
echo [5] Buka folder backup
echo [0] Keluar
echo.
set /p choice="Pilih opsi (0-5): "

if "%choice%"=="1" goto LIST
if "%choice%"=="2" goto RESTORE
if "%choice%"=="3" goto BACKUP
if "%choice%"=="4" goto CLEAN
if "%choice%"=="5" goto OPEN
if "%choice%"=="0" exit

goto MENU

REM ===============================
:LIST
python -c "import backup_system; backup_system.list_backups()"
pause
goto MENU

REM ===============================
:BACKUP
python -c "import backup_system; backup_system.backup_database()"
pause
goto MENU

REM ===============================
:RESTORE
echo.
set /p confirm="⚠️ Restore akan menimpa database sekarang. Lanjut? (y/n): "
if /I not "%confirm%"=="y" goto MENU
python -c "import backup_system; backup_system.restore_latest_backup()"
pause
goto MENU

REM ===============================
:CLEAN
python -c "import backup_system; backup_system.clean_old_backups(5)"
pause
goto MENU

REM ===============================
:OPEN
if not exist backups mkdir backups
explorer "%cd%\backups"
goto MENU
