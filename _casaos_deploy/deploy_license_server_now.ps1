# Deploy License Server ke CasaOS
# Script ini akan deploy license server dengan fitur Create License via web

$CASAOS_IP = "192.168.1.25"
$CASAOS_USER = "root"

Write-Host "🚀 Deploying License Server to CasaOS..." -ForegroundColor Cyan
Write-Host "Target: ${CASAOS_USER}@${CASAOS_IP}" -ForegroundColor Yellow
Write-Host ""

# Step 1: Remove old container if exists
Write-Host "1️⃣ Removing old container (if exists)..." -ForegroundColor White
ssh ${CASAOS_USER}@${CASAOS_IP} "docker rm -f kasir-license-server 2>/dev/null || true"

# Step 2: Create license_server directory
Write-Host "2️⃣ Creating directory..." -ForegroundColor White
ssh ${CASAOS_USER}@${CASAOS_IP} "mkdir -p ~/license_server/templates/admin ~/license_server/data"

# Step 3: Copy files
Write-Host "3️⃣ Uploading files to CasaOS..." -ForegroundColor White

# Copy main files
scp license_server/server.py ${CASAOS_USER}@${CASAOS_IP}:~/license_server/
scp license_server/Dockerfile.license ${CASAOS_USER}@${CASAOS_IP}:~/license_server/
scp license_server/docker-compose.casaos.yml ${CASAOS_USER}@${CASAOS_IP}:~/license_server/
scp license_server/requirements.license.txt ${CASAOS_USER}@${CASAOS_IP}:~/license_server/
scp license_server/.env ${CASAOS_USER}@${CASAOS_IP}:~/license_server/

# Copy templates
scp license_server/templates/admin/login.html ${CASAOS_USER}@${CASAOS_IP}:~/license_server/templates/admin/
scp license_server/templates/admin/dashboard.html ${CASAOS_USER}@${CASAOS_IP}:~/license_server/templates/admin/
scp license_server/templates/admin/create_license.html ${CASAOS_USER}@${CASAOS_IP}:~/license_server/templates/admin/

# Step 4: Deploy container
Write-Host "4️⃣ Building and starting container..." -ForegroundColor White
ssh ${CASAOS_USER}@${CASAOS_IP} "cd ~/license_server && docker compose -f docker-compose.casaos.yml up -d --build"

# Step 5: Wait for container to be ready
Write-Host "5️⃣ Waiting for container to be ready..." -ForegroundColor White
Start-Sleep -Seconds 5

# Step 6: Check status
Write-Host "6️⃣ Checking status..." -ForegroundColor White
$status = ssh ${CASAOS_USER}@${CASAOS_IP} "docker ps --filter name=kasir-license-server --format '{{.Status}}'"

if ($LASTEXITCODE -eq 0 -and $status) {
    Write-Host ""
    Write-Host "✅ Deployment successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "🌐 Admin Dashboard: http://${CASAOS_IP}:8088/admin" -ForegroundColor White
    Write-Host "👤 Username: admin" -ForegroundColor White
    Write-Host "🔑 Password: Lavansastore" -ForegroundColor White
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📝 Fitur baru:" -ForegroundColor Yellow
    Write-Host "   - Klik tombol Buat License Baru di dashboard" -ForegroundColor White
    Write-Host "   - Pilih tier (Trial/Standard/Pro/Unlimited)" -ForegroundColor White
    Write-Host "   - Generate license langsung dapat info lengkap!" -ForegroundColor White
    Write-Host ""
    Write-Host "📊 View logs:" -ForegroundColor Yellow
    Write-Host "   ssh ${CASAOS_USER}@${CASAOS_IP} `"docker logs kasir-license-server -f`"" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    Write-Host "Check logs: ssh ${CASAOS_USER}@${CASAOS_IP} `"docker logs kasir-license-server`"" -ForegroundColor Yellow
}
