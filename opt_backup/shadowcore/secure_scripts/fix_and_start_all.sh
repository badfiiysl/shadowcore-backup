#!/bin/bash
echo "🎯 FIXING PATHS & STARTING ALL SERVICES"
echo "========================================"

# Kill everything
echo "🛑 Stopping everything..."
pkill -f "python.*shadow" 2>/dev/null
pkill -f "node.*shadow" 2>/dev/null
sleep 3

# Clear all ports
echo "🔧 Clearing ports..."
for port in 8000 8001 8002 8003 8004 8006 8080 8082 8083 8020 9090 4242 8010 8090; do
    fuser -k $port/tcp 2>/dev/null
done
sleep 2

# Install deps
echo "📦 Installing dependencies..."
cd /opt/shadowcore/backend
python -m pip install uvicorn websockets flask-cors > ../logs/deps.log 2>&1

echo ""
echo "🚀 STARTING WITH CORRECT PATHS:"
echo "================================"

# Function to start service
start_service() {
    echo -n "$1 (:$2)... "
    eval "$3 > /dev/null 2>&1 &"
    sleep 2
    if timeout 2 bash -c "echo > /dev/tcp/127.0.0.1/$2" 2>/dev/null; then
        echo "✅"
    else
        echo "❌"
    fi
}

# 🐍 PYTHON SERVICES
echo ""
echo "🐍 PYTHON SERVICES:"
start_service "Main REST API" "8000" "cd /opt/shadowcore/backend && python launch_rest.py --host 0.0.0.0 --port 8000"
start_service "Threat API" "8003" "cd /opt/shadowcore/backend && python simple_threat_api.py --host 127.0.0.1 --port 8003"
start_service "Main API" "8004" "cd /opt/shadowcore/backend && python simple_main_api.py --host 127.0.0.1 --port 8004"
start_service "Auth API" "8006" "cd /opt/shadowcore/auth && python production_auth.py --host 127.0.0.1 --port 8006"
start_service "Proxy" "8080" "cd /opt/shadowcore/core && python real_proxy.py"
start_service "WebSocket" "8083" "cd /opt/shadowcore/core && python websocket_production.py"
start_service "UI Dashboard" "8020" "cd /opt/shadowcore/ui && python dashboard.py"
start_service "Threat Insight" "9090" "cd /opt/shadowcore/threat-insight && python threat-insight-api.py"

# Check for RPC Server (might be different)
if [ -f "/opt/shadowcore/backend/rpc/server.py" ]; then
    start_service "RPC Server" "4242" "cd /opt/shadowcore/backend && python rpc/server.py"
else
    echo "RPC Server (4242)... ❌ (server.py not found)"
fi

# Check for temp dashboard
if [ -f "/tmp/dashboard_8010.py" ]; then
    start_service "Temp Dashboard" "8010" "cd /tmp && python dashboard_8010.py"
else
    echo "Temp Dashboard (8010)... ⚠️ (not in /tmp)"
fi

# Check for threat intel
if [ -f "/tmp/threat_intel_simple.py" ]; then
    start_service "Threat Intel" "8090" "cd /tmp && python threat_intel_simple.py"
else
    echo "Threat Intel (8090)... ⚠️ (not in /tmp)"
fi

# 🟢 NODE.JS SERVICES
echo ""
echo "🟢 NODE.JS SERVICES:"
start_service "ShadowSearch" "8002" "cd /opt/shadowcore/shadowsearch && node simple_8002.js"
start_service "ShadowBrain" "8001" "cd /opt/shadowcore/shadowbrain && node working-api.js"
start_service "Electron Server" "8082" "cd /opt/shadowcore/electron && node pure-server.js"

# 🛠️ INFRASTRUCTURE
echo ""
echo "🛠️ INFRASTRUCTURE (checking):"
check_infra() {
    if timeout 1 bash -c "echo > /dev/tcp/127.0.0.1/$2" 2>/dev/null; then
        echo "✅ $1 (:$2) - RUNNING"
    else
        echo "🔴 $1 (:$2) - STOPPED"
    fi
}

check_infra "PostgreSQL" "5432"
check_infra "Redis" "6379"
check_infra "Neo4j HTTP" "7474"
check_infra "Neo4j Bolt" "7687"
check_infra "Ollama" "11434"
check_infra "Grafana" "3000"
check_infra "Node Exporter" "9100"
check_infra "Containerd" "42001"

echo ""
echo "📊 FINAL STATUS:"
echo "================"
sleep 3

# Quick health check
echo "Service Ports:"
for port in 8000 8001 8002 8003 8004 8006 8080 8082 8083 8020 9090; do
    if timeout 1 bash -c "echo > /dev/tcp/127.0.0.1/$port" 2>/dev/null; then
        echo "🟢 :$port"
    else
        echo "🔴 :$port"
    fi
done

echo ""
echo "🧪 Testing endpoints:"
test_endpoint() {
    if curl -s --max-time 3 "http://127.0.0.1:$1" > /dev/null 2>&1; then
        echo "✅ Port $1 responding"
    else
        echo "🔴 Port $1 not responding"
    fi
}

test_endpoint 8000  # Main API
test_endpoint 8020  # Dashboard
test_endpoint 8080  # Proxy
test_endpoint 3000  # Grafana
