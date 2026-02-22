# Quick Deploy License Server to CasaOS
# Jalankan command ini satu-per-satu dan masukkan password root saat diminta

Write-Host "=== Deploy License Server ke CasaOS ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Stop semua container yang pakai port 8088
Write-Host "1. Stopping containers on port 8088..." -ForegroundColor Yellow
ssh root@192.168.1.25 "docker ps -a | grep ':8088' | awk '{print `$1}' | xargs -r docker rm -f"

# Step 2: Remove folder lama
Write-Host "2. Removing old folder..." -ForegroundColor Yellow  
ssh root@192.168.1.25 "rm -rf ~/license_server"

# Step 3: Clone repo dari GitHub (paling baru)
Write-Host "3. Cloning repo from GitHub..." -ForegroundColor Yellow
ssh root@192.168.1.25 "git clone --depth 1 https://github.com/Indralavansa/Kasir-app.git /tmp/kasir && cp -r /tmp/kasir/license_server ~/ && rm -rf /tmp/kasir"

# Step 4: Upload .env
Write-Host "4. Uploading .env..." -ForegroundColor Yellow
scp license_server/.env root@192.168.1.25:~/license_server/

# Step 5: Deploy
Write-Host "5. Deploying container..." -ForegroundColor Yellow
ssh root@192.168.1.25 "cd ~/license_server && docker compose -f docker-compose.casaos.yml up -d --build"

# Step 6: Check status
Write-Host ""
Write-Host "6. Checking status..." -ForegroundColor Yellow
ssh root@192.168.1.25 "docker ps --filter name=kasir-license-server"

Write-Host ""
Write-Host "=== DONE ===" -ForegroundColor Green
Write-Host "Dashboard: http://192.168.1.25:8088/admin" -ForegroundColor Cyan
Write-Host "Login: admin / Lavansastore" -ForegroundColor Cyan
