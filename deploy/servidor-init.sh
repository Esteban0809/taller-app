#!/bin/bash
# Prepara un servidor Amazon Linux 2023 desde cero y arranca Taller App.
# Se usa como "user data" de EC2: se ejecuta una sola vez, como root, en el primer arranque.
# Variables que se rellenan al lanzar la instancia:
#   RAMA     rama de git a desplegar
#   IP_FIJA  IP elástica del servidor (para el dominio <ip>.sslip.io)
set -euxo pipefail

RAMA="${RAMA:-main}"
REPO="https://github.com/Esteban0809/taller-app.git"
DIR=/opt/taller-app

# 2 GB de swap: con 1 GB de RAM, MySQL + compilar el frontend se queda corto
if [ ! -f /swapfile ]; then
  dd if=/dev/zero of=/swapfile bs=1M count=2048
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo "/swapfile swap swap defaults 0 0" >> /etc/fstab
fi

dnf install -y docker git
systemctl enable --now docker

# Docker Compose y Buildx no vienen en los paquetes de Amazon Linux
mkdir -p /usr/local/lib/docker/cli-plugins
COMPOSE_VERSION=v5.6.0
BUILDX_VERSION=v0.37.2
curl -fsSL "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-linux-aarch64" \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
curl -fsSL "https://github.com/docker/buildx/releases/download/${BUILDX_VERSION}/buildx-${BUILDX_VERSION}.linux-arm64" \
  -o /usr/local/lib/docker/cli-plugins/docker-buildx
chmod +x /usr/local/lib/docker/cli-plugins/*

git clone --branch "$RAMA" "$REPO" "$DIR"
cd "$DIR/deploy"

# Secretos generados aquí: nunca salen del servidor
if [ ! -f .env ]; then
  umask 077
  cat > .env <<EOF
DB_PASSWORD=$(openssl rand -hex 24)
DB_ROOT_PASSWORD=$(openssl rand -hex 24)
JWT_SECRET=$(openssl rand -hex 32)
DOMINIO=${IP_FIJA//./-}.sslip.io
EOF
fi

docker compose -f docker-compose.prod.yml up -d --build
