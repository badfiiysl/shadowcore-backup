#!/bin/bash
echo "⚡ Quick Start - Essentials Only"
echo "================================"

# Kill everything
pkill -f "python.*shadow" 2>/dev/null
pkill -f "node.*shadow" 2>/dev/null
sleep 2

# Install missing deps
cd /opt/shadowcore/backend
venv/bin/pip install uvicorn websockets flask-cors > /dev/null 2>&1

echo "Starting essential services..."

# Start just the working ones
cd /opt/shadowcore/core && nohup ../backend/venv/bin/python real_proxy.py > ../logs/proxy.log 2>&1 &
sleep 2

cd /opt/shadowcore/ui && nohup ../backend/venv/bin/python dashboard.py > ../logs/dashboard.log 2>&1 &
sleep 2

cd /opt/shadowcore/electron && nohup node pure-server.js > ../logs/electron.log 2>&1 &
sleep 2

echo "✅ Essentials started!"
echo ""
echo "Ports:"
for port in 8080 8020 8082; do
    if timeout 1 bash -c "echo > /dev/tcp/127.0.0.1/$port" 2>/dev/null; then
        echo "🟢 :$port"
    else
        echo "🔴 :$port"
    fi
done

echo ""
echo "Test:"
curl -s http://127.0.0.1:8080 > /dev/null && echo "✅ Proxy works" || echo "❌ Proxy down"
curl -s http://127.0.0.1:8020 > /dev/null && echo "✅ Dashboard works" || echo "❌ Dashboard down"
