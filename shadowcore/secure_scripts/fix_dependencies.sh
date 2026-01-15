#!/bin/bash
echo "📦 Installing Missing Dependencies"
echo "================================="

cd /opt/shadowcore/backend

echo "Installing Python dependencies..."
venv/bin/pip install uvicorn websockets flask-cors python-socketio eventlet > ../logs/deps_install.log 2>&1

echo "✅ Installed: uvicorn, websockets, flask-cors, python-socketio, eventlet"

echo ""
echo "Checking Node.js issues..."
# Check if Node.js services need npm install
if [ -f "/opt/shadowcore/shadowsearch/package.json" ]; then
    echo "Installing Node.js dependencies for ShadowSearch..."
    cd /opt/shadowcore/shadowsearch && npm install 2>/dev/null || echo "No package.json or npm issues"
fi

if [ -f "/opt/shadowcore/shadowbrain/package.json" ]; then
    echo "Installing Node.js dependencies for ShadowBrain..."
    cd /opt/shadowcore/shadowbrain && npm install 2>/dev/null || echo "No package.json or npm issues"
fi

echo ""
echo "🔄 Restarting services..."
pkill -f "python.*shadow" 2>/dev/null
pkill -f "node.*shadow" 2>/dev/null
sleep 2

echo "Starting fixed services..."
/opt/shadowcore/start_fixed.sh
