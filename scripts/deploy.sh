#!/bin/bash
# deploy.sh — Clone repo (if needed) and launch the full stack
set -euo pipefail

REPO_URL="https://github.com/AlexanderDimichele/csc466-docker-mongo"
APP_DIR="$HOME/csc466-docker-mongo"

echo "=== Deploying Video Game App ==="

# Clone only if the directory doesn't exist yet
if [ ! -d "$APP_DIR" ]; then
    echo "Cloning repository..."
    git clone "$REPO_URL" "$APP_DIR"
else
    echo "Repository already present — pulling latest changes..."
    git -C "$APP_DIR" pull
fi

cd "$APP_DIR"

echo "=== Building and starting containers ==="
docker compose down --remove-orphans 2>/dev/null || true
docker compose up --build -d

echo ""
echo "✅  Stack is up."
echo "    Web app → http://$(curl -s ifconfig.me):8080"
echo "    Logs    → docker compose logs -f"

