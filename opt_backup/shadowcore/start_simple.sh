#!/bin/bash
echo "⚡ SIMPLE SHADOWCORE START"
echo "========================"

cd /opt/shadowcore

# Kill everything
echo "Killing old processes..."
pkill -f "python.*shadow" 2>/dev/null
pkill -f "node.*shadow" 2>/dev/null
sleep 2

echo ""
echo "Starting services from correct directories..."

# Change to each directory and start services
echo "1. Starting UI Dashboard (8020)..."
cd ui && python dashboard.py > ../logs/dashboard.log 2>&1 &
cd ..
sleep 1

echo "2. Starting Proxy (8080)..."
cd core && python real_proxy.py > ../logs/proxy.log 2>&1 &
cd ..
sleep 1

echo "3. Starting Threat API (8003)..."
cd backend && python simple_threat_api.py --host 127.0.0.1 --port 8003 > ../logs/threat_api.log 2>&1 &
cd ..
sleep 1

echo "4. Starting Main API (8004)..."
cd backend && python simple_main_api.py --host 127.0.0.1 --port 8004 > ../logs/main_api.log 2>&1 &
cd ..
sleep 1

echo "5. Starting Auth API (8006)..."
cd auth && python production_auth.py --host 127.0.0.1 --port 8006 > ../logs/auth.log 2>&1 &
cd ..
sleep 1

echo "6. Starting WebSocket (8083)..."
cd core && python websocket_production.py > ../logs/websocket.log 2>&1 &
cd ..
sleep 1

echo "7. Starting Threat Insight (9090)..."
cd threat-insight && python threat-insight-api.py > ../logs/insight.log 2>&1 &
cd ..
sleep 1

# Fix Main REST API first
echo "8. Creating/fixing Main REST API (8000)..."
cd backend
# Ensure rest module exists
if [ ! -d "rest" ]; then
    mkdir -p rest
    cat > rest/api.py << 'API'
from fastapi import FastAPI
app = FastAPI()
@app.get("/")
def root(): return {"service": "ShadowCore"}
@app.get("/health")
def health(): return {"status": "healthy"}
API
    touch rest/__init__.py
fi

echo "Starting Main REST API..."
python launch_rest.py --host 0.0.0.0 --port 8000 > ../logs/main_rest.log 2>&1 &
cd ..
sleep 3

echo ""
echo "⏳ Waiting 5 seconds for startup..."
sleep 5

echo ""
echo "📊 STATUS CHECK:"
echo "================"

check_port() {
    if timeout 1 bash -c "echo > /dev/tcp/127.0.0.1/$1" 2>/dev/null; then
        echo "🟢 Port $1: OPEN"
        return 0
    else
        echo "🔴 Port $1: CLOSED"
        return 1
    fi
}

check_port 8000  # Main REST API
check_port 8003  # Threat API
check_port 8004  # Main API
check_port 8006  # Auth API
check_port 8080  # Proxy
check_port 8083  # WebSocket
check_port 8020  # UI Dashboard
check_port 9090  # Threat Insight

echo ""
echo "🧪 Quick tests:"
curl -s http://127.0.0.1:8000/health 2>/dev/null | grep -q "healthy" && echo "✅ Main API healthy" || echo "❌ Main API down"
curl -s http://127.0.0.1:8020 2>/dev/null && echo "✅ Dashboard reachable" || echo "❌ Dashboard down"
curl -s http://127.0.0.1:8080 2>/dev/null && echo "✅ Proxy reachable" || echo "❌ Proxy down"

echo ""
echo "📈 Process count:"
ps aux | grep -E "(python|node).*shadow" | grep -v grep | wc -l
