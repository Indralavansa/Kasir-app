@echo off
chcp 65001 > nul
echo ==========================================
echo   KASIR TOKO SEMBAKO - START APPLICATION
echo ==========================================
echo.

REM Change to parent directory (project root)
cd /d "%~dp0\.."

REM Load .env file environment variables
if exist .env (
    for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
        if not "%%b"=="" (
            set "%%a=%%b"
        )
    )
)

REM Run app directly with Python
echo Starting application...
python app/app_simple.py

pause
