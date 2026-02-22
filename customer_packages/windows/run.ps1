param()
$ErrorActionPreference = 'Stop'

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here

if (-not (Test-Path .env)) {
  Write-Error "Missing .env. Copy .env.example to .env and fill it."
}

# Ensure instance folder exists
if (-not (Test-Path instance)) {
  New-Item -ItemType Directory -Path instance | Out-Null
}

# Start

docker compose -f docker-compose.localhost.yml --env-file .env up -d

Write-Output "OK: http://127.0.0.1:5000"
Write-Output "Jika lisensi belum aktif: http://127.0.0.1:5000/license"
