#!/usr/bin/env bash
# Pull the latest code, rebuild the sandbox runner images and the app, and
# restart the stack. Safe to re-run; used for first deploy and every update.
#
#   cd /opt/ai-tutor && ./deploy/deploy.sh

set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  echo "Missing .env — run: cp .env.hetzner.example .env and fill it in." >&2
  exit 1
fi

for var in DOMAIN ACME_EMAIL POSTGRES_PASSWORD JWT_SECRET; do
  if ! grep -Eq "^${var}=[^[:space:]#]+" .env; then
    echo "$var is empty in .env" >&2
    exit 1
  fi
done

echo "==> Pulling latest code"
git pull --ff-only

echo "==> Building sandbox runner images"
docker build -t ai-tutor-runner-python:latest ./docker/runner-python
docker build -t ai-tutor-runner-java:latest ./docker/runner-java
docker build -t ai-tutor-runner-ruby:latest ./docker/runner-ruby

echo "==> Building and starting the app"
docker compose -f docker-compose.prod.yml up -d --build --remove-orphans

echo "==> Cleaning up old images"
docker image prune -f >/dev/null

echo "==> Waiting for the API"
DOMAIN=$(grep -E '^DOMAIN=' .env | cut -d= -f2-)
for _ in $(seq 1 30); do
  if docker compose -f docker-compose.prod.yml exec -T backend \
       python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" 2>/dev/null; then
    echo "Up: https://$DOMAIN"
    exit 0
  fi
  sleep 2
done

echo "Backend didn't become healthy — check: docker compose -f docker-compose.prod.yml logs backend" >&2
exit 1
