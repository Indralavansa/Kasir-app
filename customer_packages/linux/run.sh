#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -f .env ]; then
  echo "Missing .env. Copy .env.example to .env and fill it." >&2
  exit 1
fi

mkdir -p instance

docker compose -f docker-compose.localhost.yml --env-file .env up -d

echo "OK: http://127.0.0.1:5000"
echo "Jika lisensi belum aktif: http://127.0.0.1:5000/license"
