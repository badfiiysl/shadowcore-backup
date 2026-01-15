#!/bin/bash
echo "🚀 ShadowCore - Complete Fixed Startup"
echo "======================================"

cd /opt/shadowcore

# Install ALL required dependencies first
echo "📦 Ensuring all dependencies are installed..."
cd backend && venv/bin/pip install uvicorn websockets flask-cors python-socketio eventlet fastapi flask psutil requests > ../logs/deps_fix.log 2>&1

# Kill everything first
echo "🛑 Stopping everything..."
pkill -f "python.*shadow" 2>/dev/null
pkill -f "node.*shadow" 2>/dev/null
sleep 3

# Fix port conflicts
echo "🔧 Clearing port conflicts..."
for port in 8000 8001 8002 8003 8004 8006 8080 8082 8083 8020 9090; do
    fuser -k $port/tcp 2>/dev/null
done
sleep 2

echo ""
echo "Starting services in order..."

# 1. Start FastAPI services (uvicorn based)
start_fastapi() {
    local name="$1"
    local dir="$2"
    local file="$3"
    local port="$4"
    
    echo -n "Starting $name... "
    cd "$dir" && nohup ../backend/venv/bin/uvicorn "$file" --host 0.0.0.0 --port "$port" > "../logs/${name// /_}.log" 2>&1 &
    sleep 3
    if timeout 2 bash -c "echo > /dev/tcp/127.0.0.1/$port" 2>/dev/null; then
        echo "✅"
    else
        echo "❌ (check logs)"
    fi
}

# 2. Start Flask services
start_flask() {
    local name="$1"
    local dir="$2"
    local file="$3"
    local port="$4"
    
    echo -n "Starting $name... "
    cd "$dir" && nohup ../backend/venv/bin/python "$file" > "../logs/${name// /_}.log" 2>&1 &
    sleep 3
    if timeout 2 bash -c "echo > /dev/tcp/127.0.0.1/$port" 2>/dev/null; then
        echo "✅"
    else
        echo "❌ (check logs)"
    fi
}

# 3. Start Node.js services
start_node() {
    local name="$1"
    local dir="$2"
    local file="$3"
    local port="$4"
    
    echo -n "Starting $name... "
    cd "$dir" && nohup node "$file" > "../logs/${name// /_}.log" 2>&1 &
    sleep 3
    if timeout 2 bash -c "echo > /dev/tcp/127.0.0.1/$port" 2>/dev/null; then
        echo "✅"
    else
        echo "❌ (check logs)"
    fi
}

# Start services
start_fastapi "Main REST API" "backend" "launch_rest:app" 8000
start_fastapi "Auth API" "auth" "production_auth:app" 8006

start_flask "Threat API" "backend" "simple_threat_api.py" 8003
start_flask "Main API" "backend" "simple_main_api.py" 8004
start_flask "Proxy" "core" "real_proxy.py" 8080
start_flask "WebSocket" "core" "websocket_production.py" 8083
start_flask "UI Dashboard" "ui" "dashboard.py" 8020
start_flask "Threat Insight" "threat-insight" "threat-insight-api.py" 9090

start_node "ShadowSearch" "shadowsearch" "simple_8002.js" 8002
start_node "ShadowBrain" "shadowbrain" "working-api.js" 8001
start_node "Electron" "electron" "pure-server.js" 8082

echo ""
echo "📊 Health Check:"
echo "--------------"
sleep 2
bash /opt/shadowcore/health.sh

echo ""
echo "🧪 Quick Tests:"
test_endpoint() {
    local url=$1
    local name=$2
    echo -n "$name: "
    if curl -s --max-time 3 "$url" > /dev/null 2>&1; then
        echo "✅"
    else
        echo "❌"
    fi
}

test_endpoint "http://127.0.0.1:8000" "Main API"
test_endpoint "http://127.0.0.1:8020" "Dashboard"
test_endpoint "http://127.0.0.1:8080" "Proxy"
