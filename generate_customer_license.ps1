# Script untuk Generate License untuk Customer
# Usage: .\generate_customer_license.ps1 standard
# Usage: .\generate_customer_license.ps1 trial 30
# Usage: .\generate_customer_license.ps1 pro
# Usage: .\generate_customer_license.ps1 unlimited

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('trial','standard','pro','unlimited')]
    [string]$Tier,
    
    [int]$Days = 30
)

$CASAOS_IP = "192.168.1.25"
$CASAOS_USER = "lavansa"  # Sesuaikan dengan user SSH CasaOS Anda

Write-Host "🔑 Generating $Tier license..." -ForegroundColor Cyan

if ($Tier -eq "trial") {
    $cmd = "docker exec kasir-license-server python admin_create_license.py trial --days $Days"
} else {
    $cmd = "docker exec kasir-license-server python admin_create_license.py $Tier"
}

Write-Host "Executing on CasaOS: $cmd" -ForegroundColor Yellow

# Execute via SSH
$result = ssh ${CASAOS_USER}@${CASAOS_IP} $cmd

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ License generated successfully!" -ForegroundColor Green
    Write-Host $result -ForegroundColor White
    Write-Host "`n📋 Copy license key di atas dan kirim ke customer" -ForegroundColor Cyan
    Write-Host "Plus kasih juga:" -ForegroundColor Yellow
    Write-Host "LICENSE_SERVER_PUBLIC_KEY_B64=FubZG4q/E7a8W9V1Ys6bYoZKPQYv7iYPq6S1Ay8phII=" -ForegroundColor White
} else {
    Write-Host "`n❌ Error generating license!" -ForegroundColor Red
    Write-Host "Cek apakah:" -ForegroundColor Yellow
    Write-Host "1. Container 'kasir-license-server' sudah running di CasaOS" -ForegroundColor White
    Write-Host "2. SSH ke CasaOS bisa akses tanpa password (gunakan ssh-keygen)" -ForegroundColor White
}
