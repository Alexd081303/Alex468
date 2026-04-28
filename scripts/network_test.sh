#!/bin/bash
# network_test.sh — Verify inter-container connectivity and port publishing
set -euo pipefail

echo "=== Network Tests ==="

echo ""
echo "--- [1] Containers currently running ---"
docker compose ps

echo ""
echo "--- [2] Ping mongo from the app container ---"
docker compose exec app sh -c "ping -c 3 mongo" && echo "✅  DNS resolution: app → mongo OK" || echo "❌  DNS resolution failed"

echo ""
echo "--- [3] Check MongoDB port reachable from app container ---"
docker compose exec app sh -c \
    "node -e \"const net=require('net'); const s=net.connect(27017,'mongo',()=>{console.log('✅  TCP 27017 open');s.destroy()}); s.on('error',e=>{console.error('❌ ',e.message);process.exit(1)});\""

echo ""
echo "--- [4] Check web app responds on host port 8080 ---"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080 || true)
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✅  HTTP $HTTP_CODE — web app is reachable on port 8080"
else
    echo "⚠️   HTTP $HTTP_CODE — unexpected response on port 8080"
fi

echo ""
echo "--- [5] Confirm MongoDB port is NOT reachable from the host ---"
if ! nc -z -w2 localhost 27017 2>/dev/null; then
    echo "✅  Port 27017 correctly NOT exposed to host"
else
    echo "⚠️   Port 27017 is exposed to host — consider removing the port mapping"
fi

echo ""
echo "=== Network tests complete ==="

