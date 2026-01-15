#!/bin/bash
cd /opt/shadowcore

echo "🚀 Starting ShadowCore..."

# Start Python services
cd backend && venv/bin/python launch_rest.py --host 0.0.0.0 --port 8000 > ../logs/main_api.log 2>&1 &
cd backend && venv/bin/python simple_threat_api.py --host 127.0.0.1 --port 8003 > ../logs/threat_api.log 2>&1 &
cd backend && venv/bin/python simple_main_api.py --host 127.0.0.1 --port 8004 > ../logs/main_api2.log 2>&1 &
cd auth && ../backend/venv/bin/python production_auth.py --host 127.0.0.1 --port 8006 > ../logs/auth.log 2>&1 &
cd core && ../backend/venv/bin/python real_proxy.py > ../logs/proxy.log 2>&1 &
cd core && ../backend/venv/bin/python websocket_production.py > ../logs/websocket.log 2>&1 &
cd ui && ../backend/venv/bin/python dashboard.py > ../logs/dashboard.log 2>&1 &
cd threat-insight && ../backend/venv/bin/python threat-insight-api.py > ../logs/insight.log 2>&1 &

# Start Node.js services
cd shadowsearch && node simple_8002.js > ../logs/search.log 2>&1 &
cd shadowbrain && node working-api.js > ../logs/brain.log 2>&1 &
cd electron && node pure-server.js > ../logs/electron.log 2>&1 &

echo "✅ Services started!"
echo "📊 Check logs: ls -la /opt/shadowcore/logs/"
echo "🔍 Check ports: netstat -tulpn | grep -E '8000|8001|8002|8003|8004|8006|8080|8082|8083|8020|9090'"
