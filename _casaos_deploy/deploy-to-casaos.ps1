# Script Deploy ke CasaOS STB
# IP STB: 192.168.1.25

$STB_IP = "192.168.1.25"
$STB_USER = "casaos"
$STB_PATH = "/DATA/AppData/kasir-app"
$LOCAL_PATH = $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Deploy Kasir App ke CasaOS STB" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "STB IP: $STB_IP" -ForegroundColor Yellow
Write-Host "Target Path: $STB_PATH" -ForegroundColor Yellow
Write-Host ""

# Cek koneksi ke STB
Write-Host "[1/4] Checking connection to STB..." -ForegroundColor Green
$ping = Test-Connection -ComputerName $STB_IP -Count 2 -Quiet
if (-not $ping) {
    Write-Host "ERROR: Tidak bisa connect ke $STB_IP" -ForegroundColor Red
    Write-Host "Pastikan STB menyala dan terhubung ke jaringan yang sama" -ForegroundColor Yellow
    exit 1
}
Write-Host "OK - STB online!" -ForegroundColor Green
Write-Host ""

# Pilih metode transfer
Write-Host "[2/4] Pilih metode transfer:" -ForegroundColor Green
Write-Host "1. SCP (Butuh SSH access)" -ForegroundColor Cyan
Write-Host "2. Manual via CasaOS Files (Recommended)" -ForegroundColor Cyan
Write-Host ""
$choice = Read-Host "Pilih (1/2)"

if ($choice -eq "1") {
    # Transfer via SCP
    Write-Host ""
    Write-Host "[3/4] Transfer files via SCP..." -ForegroundColor Green
    Write-Host "Masukkan password CasaOS saat diminta" -ForegroundColor Yellow
    Write-Host ""
    
    # Cek scp command tersedia
    $scpExists = Get-Command scp -ErrorAction SilentlyContinue
    if (-not $scpExists) {
        Write-Host "ERROR: SCP tidak tersedia. Install OpenSSH Client atau gunakan metode manual." -ForegroundColor Red
        exit 1
    }
    
    # Create remote directory first
    Write-Host "Creating remote directory..." -ForegroundColor Cyan
    ssh "${STB_USER}@${STB_IP}" "mkdir -p $STB_PATH"
    
    # Transfer files (exclude unnecessary files)
    Write-Host "Transferring files (ini bisa memakan waktu beberapa menit)..." -ForegroundColor Cyan
    scp -r -o "StrictHostKeyChecking=no" "$LOCAL_PATH\app" "$LOCAL_PATH\backups" "$LOCAL_PATH\data" "$LOCAL_PATH\instance" "$LOCAL_PATH\migrations" "$LOCAL_PATH\scripts" "$LOCAL_PATH\Dockerfile" "$LOCAL_PATH\docker-compose.yml" "$LOCAL_PATH\requirements.txt" "${STB_USER}@${STB_IP}:${STB_PATH}/"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Transfer gagal!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "OK - Transfer selesai!" -ForegroundColor Green
    Write-Host ""
    
    # Deploy via SSH
    Write-Host "[4/4] Deploying container..." -ForegroundColor Green
    Write-Host "Masukkan password CasaOS lagi untuk deploy" -ForegroundColor Yellow
    Write-Host ""
    
    ssh "${STB_USER}@${STB_IP}" "cd $STB_PATH && docker-compose up -d --build"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "   DEPLOY BERHASIL!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Akses aplikasi di:" -ForegroundColor Cyan
        Write-Host "http://${STB_IP}:5000" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Login:" -ForegroundColor Cyan
        Write-Host "  Admin: admin / admin123" -ForegroundColor White
        Write-Host "  Kasir: kasir / kasir123" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host "ERROR: Deploy gagal!" -ForegroundColor Red
        Write-Host "Coba manual: ssh ${STB_USER}@${STB_IP}" -ForegroundColor Yellow
        exit 1
    }
    
} else {
    # Manual method
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "   INSTRUKSI MANUAL" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Buka CasaOS di browser:" -ForegroundColor Cyan
    Write-Host "   http://${STB_IP}" -ForegroundColor White
    Write-Host ""
    Write-Host "2. Klik 'Files' app" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "3. Navigate ke: /DATA/AppData/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "4. Buat folder baru: 'kasir-app'" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "5. Upload semua file dari:" -ForegroundColor Cyan
    Write-Host "   $LOCAL_PATH" -ForegroundColor White
    Write-Host ""
    Write-Host "6. Setelah upload selesai, buka Terminal di CasaOS" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "7. Jalankan commands:" -ForegroundColor Cyan
    Write-Host "   cd /DATA/AppData/kasir-app" -ForegroundColor White
    Write-Host "   docker-compose up -d --build" -ForegroundColor White
    Write-Host ""
    Write-Host "8. Tunggu 2-3 menit, lalu akses:" -ForegroundColor Cyan
    Write-Host "   http://${STB_IP}:5000" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Atau gunakan SSH dari PowerShell ini:" -ForegroundColor Cyan
    Write-Host "   ssh ${STB_USER}@${STB_IP}" -ForegroundColor White
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Script selesai!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
