#!/bin/bash
# setup.sh — Bootstrap Docker + Docker Compose on a CloudLab Ubuntu 22.04 node
# Usage: bash cloudlab/setup.sh
set -euo pipefail

echo "=== [1/5] Updating package index ==="
sudo apt-get update -y

echo "=== [2/5] Installing prerequisites ==="
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    make

echo "=== [3/5] Adding Docker GPG key and repository ==="
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "=== [4/5] Installing Docker Engine and Compose plugin ==="
sudo apt-get update -y
sudo apt-get install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

sudo usermod -aG docker "$USER"
sudo systemctl enable docker
sudo systemctl start docker

echo "=== [5/5] Verifying installation ==="
docker --version
docker compose version

echo ""
echo "✅  Setup complete. You may need to log out and back in for group changes to take effect."
echo "    Then run:  bash scripts/deploy.sh"

