# PowerShell script untuk Windows
# Setup Docker untuk Kasir Toko Sembako

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Kasir Toko Sembako - Docker Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
try {
    docker --version | Out-Null
    Write-Host "✅ Docker ditemukan" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker tidak ditemukan. Install Docker Desktop terlebih dahulu." -ForegroundColor Red
    Write-Host "   Download: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Check if docker-compose is installed
try {
    docker-compose --version | Out-Null
    Write-Host "✅ Docker Compose ditemukan" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose tidak ditemukan." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Create directories
Write-Host "📁 Membuat folder yang diperlukan..." -ForegroundColor Yellow
$folders = @("instance", "backups", "data")
foreach ($folder in $folders) {
    if (-not (Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
    }
}
Write-Host "✅ Folder dibuat" -ForegroundColor Green
Write-Host ""

# Check and create .env file
if (-not (Test-Path ".env")) {
    Write-Host "📝 File .env tidak ditemukan, membuat dari template..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ File .env dibuat dari .env.example" -ForegroundColor Green
        Write-Host "⚠️  PENTING: Edit file .env dan sesuaikan konfigurasi!" -ForegroundColor Yellow
    } else {
        @"
SECRET_KEY=rahasia-sangat-rahasia-123456
TELEGRAM_BOT_TOKEN=
TELEGRAM_ADMIN_CHAT_IDS=
TELEGRAM_NOTIFY_NEW_TRANSACTION=false
TELEGRAM_NOTIFY_LOW_STOCK_THRESHOLD=10
"@ | Out-File -FilePath ".env" -Encoding UTF8
        Write-Host "✅ File .env default dibuat" -ForegroundColor Green
    }
    Write-Host ""
} else {
    Write-Host "✅ File .env sudah ada" -ForegroundColor Green
    Write-Host ""
}

# Build Docker image
Write-Host "🔨 Building Docker image..." -ForegroundColor Yellow
docker-compose build
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Docker image berhasil dibuild" -ForegroundColor Green
} else {
    Write-Host "❌ Build gagal!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Start container
Write-Host "🚀 Starting container..." -ForegroundColor Yellow
docker-compose up -d
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Container berhasil distart" -ForegroundColor Green
} else {
    Write-Host "❌ Start gagal!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Show status
Write-Host "📊 Status container:" -ForegroundColor Cyan
docker-compose ps
Write-Host ""

# Get local IP
$localIP = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Ethernet*","Wi-Fi*" | Where-Object {$_.IPAddress -like "192.168.*" -or $_.IPAddress -like "10.*"} | Select-Object -First 1).IPAddress

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🎉 Setup selesai!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Akses aplikasi di:" -ForegroundColor Yellow
Write-Host "  Lokal     : http://localhost:5000" -ForegroundColor White
if ($localIP) {
    Write-Host "  Network   : http://${localIP}:5000" -ForegroundColor White
}
Write-Host ""
Write-Host "Login default:" -ForegroundColor Yellow
Write-Host "  Admin     : admin / admin123" -ForegroundColor White
Write-Host "  Kasir     : kasir / kasir123" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  PENTING: Ganti password setelah login pertama!" -ForegroundColor Red
Write-Host ""
Write-Host "Lihat logs: docker-compose logs -f" -ForegroundColor Gray
Write-Host "Stop app  : docker-compose down" -ForegroundColor Gray
Write-Host ""
