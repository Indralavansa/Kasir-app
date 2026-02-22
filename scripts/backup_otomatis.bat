@echo off
REM ========================================
REM BACKUP OTOMATIS - WINDOWS BATCH
REM ========================================
REM Script untuk menjalankan backup otomatis
REM Bisa dijalankan manual atau via Task Scheduler

setlocal enabledelayedexpansion

REM Get directory path
set SCRIPT_DIR=%~dp0
set PYTHON_CMD=python

REM Check if in virtual environment
if exist "%SCRIPT_DIR%..\venv\Scripts\python.exe" (
    set PYTHON_CMD=%SCRIPT_DIR%..\venv\Scripts\python.exe
    echo [INFO] Menggunakan Python dari virtual environment
) else if exist "%SCRIPT_DIR%..\venv\Scripts\activate.bat" (
    call "%SCRIPT_DIR%..\venv\Scripts\activate.bat"
    echo [INFO] Virtual environment activated
)

echo.
echo ========================================
echo BACKUP OTOMATIS - TOKO SEMBAKO KASIR
echo ========================================
echo.

REM Check arguments
if "%1"=="" (
    REM No arguments - show interactive menu
    "%PYTHON_CMD%" "%SCRIPT_DIR%.\..\tools\backup_otomatis_standalone.py"
) else if "%1"=="auto" (
    REM Auto backup
    echo [%date% %time%] Memulai auto backup...
    "%PYTHON_CMD%" "%SCRIPT_DIR%.\..\tools\backup_otomatis_standalone.py" auto
    echo [%date% %time%] Auto backup selesai
) else if "%1"=="produk" (
    REM Backup produk saja
    "%PYTHON_CMD%" "%SCRIPT_DIR%.\..\tools\backup_otomatis_standalone.py" produk
) else if "%1"=="transaksi" (
    REM Backup transaksi saja
    "%PYTHON_CMD%" "%SCRIPT_DIR%.\..\tools\backup_otomatis_standalone.py" transaksi
) else if "%1"=="database" (
    REM Backup database saja
    "%PYTHON_CMD%" "%SCRIPT_DIR%.\..\tools\backup_otomatis_standalone.py" database
) else if "%1"=="list" (
    REM List backups
    "%PYTHON_CMD%" "%SCRIPT_DIR%.\..\tools\backup_otomatis_standalone.py" list
) else if "%1"=="cleanup" (
    REM Cleanup old backups
    "%PYTHON_CMD%" "%SCRIPT_DIR%.\..\tools\backup_otomatis_standalone.py" cleanup
) else (
    REM Unknown command
    "%PYTHON_CMD%" "%SCRIPT_DIR%.\..\tools\backup_otomatis_standalone.py" --help
)

echo.
endlocal
pause
