#!/usr/bin/env bash
# One-time provisioning for a fresh Hetzner Cloud server (Ubuntu 24.04).
# Run as root:
#
#   curl -fsSL https://raw.githubusercontent.com/Karthiga08/ai-power-coding-tutor/main/deploy/server-setup.sh | bash
#
# Installs Docker, opens only SSH/HTTP/HTTPS, adds swap (the Java runner and
# the frontend build both like headroom), creates a `deploy` user, and clones
# the repo into /opt/ai-tutor.

set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/Karthiga08/ai-power-coding-tutor.git}"
APP_DIR="${APP_DIR:-/opt/ai-tutor}"
DEPLOY_USER="${DEPLOY_USER:-deploy}"

if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root." >&2
  exit 1
fi

echo "==> Updating packages"
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get upgrade -y
apt-get install -y ca-certificates curl git ufw unattended-upgrades fail2ban

echo "==> Installing Docker"
if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sh
fi
systemctl enable --now docker

echo "==> Firewall (ssh, http, https)"
ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 443/udp
ufw --force enable

echo "==> Swap (2G)"
if ! swapon --show | grep -q /swapfile; then
  fallocate -l 2G /swapfile
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

echo "==> Deploy user"
if ! id "$DEPLOY_USER" >/dev/null 2>&1; then
  adduser --disabled-password --gecos "" "$DEPLOY_USER"
fi
usermod -aG docker "$DEPLOY_USER"
if [ -f /root/.ssh/authorized_keys ]; then
  install -d -m 700 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "/home/$DEPLOY_USER/.ssh"
  install -m 600 -o "$DEPLOY_USER" -g "$DEPLOY_USER" /root/.ssh/authorized_keys "/home/$DEPLOY_USER/.ssh/authorized_keys"
fi

echo "==> Cloning app into $APP_DIR"
if [ ! -d "$APP_DIR/.git" ]; then
  git clone "$REPO_URL" "$APP_DIR"
fi
chown -R "$DEPLOY_USER:$DEPLOY_USER" "$APP_DIR"

echo
echo "Done. Next:"
echo "  su - $DEPLOY_USER"
echo "  cd $APP_DIR && cp .env.hetzner.example .env && nano .env"
echo "  ./deploy/deploy.sh"
