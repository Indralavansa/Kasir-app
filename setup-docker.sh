#!/bin/bash
# Setup script untuk deployment di CasaOS/Docker
# 
# Usage: bash setup-docker.sh

set -e

echo "=========================================="
echo "Kasir Toko Sembako - Docker Setup"
echo "=========================================="
echo ""

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker tidak ditemukan. Install Docker terlebih dahulu."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose tidak ditemukan. Install Docker Compose terlebih dahulu."
    exit 1
fi

echo "✅ Docker dan Docker Compose ditemukan"
echo ""

# Create directories if not exist
echo "📁 Membuat folder yang diperlukan..."
mkdir -p instance backups data
echo "✅ Folder dibuat"
echo ""

# Check if .env exists, if not create from example
if [ ! -f .env ]; then
    echo "📝 File .env tidak ditemukan, membuat dari template..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ File .env dibuat dari .env.example"
        echo "⚠️  PENTING: Edit file .env dan sesuaikan konfigurasi!"
        echo ""
    else
        echo "⚠️  File .env.example tidak ditemukan, membuat .env default..."
        cat > .env << 'EOF'
SECRET_KEY=rahasia-sangat-rahasia-123456
TELEGRAM_BOT_TOKEN=
TELEGRAM_ADMIN_CHAT_IDS=
TELEGRAM_NOTIFY_NEW_TRANSACTION=false
TELEGRAM_NOTIFY_LOW_STOCK_THRESHOLD=10
EOF
        echo "✅ File .env default dibuat"
        echo ""
    fi
else
    echo "✅ File .env sudah ada"
    echo ""
fi

# Build the Docker image
echo "🔨 Building Docker image..."
docker-compose build
echo "✅ Docker image berhasil dibuild"
echo ""

# Start the container
echo "🚀 Starting container..."
docker-compose up -d
echo "✅ Container berhasil distart"
echo ""

# Show status
echo "📊 Status container:"
docker-compose ps
echo ""

# Show logs
echo "📝 Log terakhir (Ctrl+C untuk keluar):"
echo "=========================================="
docker-compose logs -f --tail=50
