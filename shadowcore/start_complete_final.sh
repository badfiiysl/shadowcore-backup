#!/bin/bash
echo "🏁 SHADOWCORE COMPLETE STARTUP"
echo "=============================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd /opt/shadowcore

# Stop everything
echo "🛑 Stopping existing services..."
pkill -f "python.*shadow" 2>/dev/null
pkill -f "node.*shadow" 2>/dev/null
sleep 2

# Clear ports
echo "🔧 Clearing ports..."
for port in 8000 8001 8002 8003 8004 8006 8080 8082 8083 8020 9090; do
    fuser -k $port/tcp 2>/dev/null
done
sleep 1

echo ""
echo "🚀 Starting ShadowCore Platform..."
echo "--------------------------------"

# Ensure rest module exists
if [ ! -f "backend/rest/api.py" ]; then
    echo "Creating missing rest module..."
    mkdir -p backend/rest
    cat > backend/rest/api.py << 'RESTAPI'
from fastapi import FastAPI
import datetime
app = FastAPI(title="ShadowCore REST API")
@app.get("/")
def root(): return {"service": "ShadowCore", "status": "running"}
@app.get("/health")
def health(): return {"status": "healthy", "timestamp": datetime.datetime.now().isoformat()}
RESTAPI
    touch backend/rest/__init__.py
fi

# Start services with error handling
start_service() {
    local name="$1"
    local cmd="$2"
    local port="$3"
    
    echo -n "$name (:${port})... "
    
    # Kill any existing
    pkill -f "$(echo "$cmd" | awk '{print $1}')" 2>/dev/null
    
    # Start
    eval "nohup $cmd > logs/${name// /_}.log 2>&1 &"
    sleep 2
    
    # Check
    if timeout 2 bash -c "echo > /dev/tcp/127.0.0.1/$port" 2>/dev/null; then
        echo -e "${GREEN}✅${NC}"
        return 0
    else
        echo -e "${RED}❌${NC}"
        return 1
    fi
}

echo ""
echo "🐍 Python Services:"

start_service "Main REST API" "cd backend && python launch_rest.py --host 0.0.0.0 --port 8000" 8000
start_service "Threat API" "cd backend && python simple_threat_api.py --host 127.0.0.1 --port 8003" 8003
start_service "Main API" "cd backend && python simple_main_api.py --host 127.0.0.1 --port 8004" 8004
start_service "Auth API" "cd auth && python production_auth.py --host 127.0.0.1 --port 8006" 8006
start_service "Proxy" "cd core && python real_proxy.py" 8080
start_service "WebSocket" "cd core && python websocket_production.py" 8083
start_service "UI Dashboard" "cd ui && python dashboard.py" 8020
start_service "Threat Insight" "cd threat-insight && python threat-insight-api.py" 9090

echo ""
echo "🟢 Node.js Services:"

# Try Node.js services but don't fail if they don't work
cd shadowsearch && [ -f "simple_8002.js" ] && nohup node simple_8002.js > ../logs/shadowsearch.log 2>&1 &
echo "ShadowSearch (:8002)... ${YELLOW}⚠️ Attempted${NC}"
sleep 1

cd ../shadowbrain && [ -f "working-api.js" ] && nohup node working-api.js > ../logs/shadowbrain.log 2>&1 &
echo "ShadowBrain (:8001)... ${YELLOW}⚠️ Attempted${NC}"
sleep 1

cd ../electron && [ -f "pure-server.js" ] && nohup node pure-server.js > ../logs/electron.log 2>&1 &
echo "Electron (:8082)... ${YELLOW}⚠️ Attempted${NC}"

echo ""
echo "⏳ Waiting for services to stabilize..."
sleep 5

echo ""
echo "📊 FINAL STATUS:"
echo "================"

# Check all ports
ports=(
    "8000:Main REST API"
    "8003:Threat API"
    "8004:Main API"
    "8006:Auth API"
    "8080:Proxy"
    "8083:WebSocket"
    "8020:UI Dashboard"
    "9090:Threat Insight"
    "8002:ShadowSearch"
    "8001:ShadowBrain"
    "8082:Electron"
)

working=0
total=${#ports[@]}

for entry in "${ports[@]}"; do
    port="${entry%%:*}"
    name="${entry#*:}"
    
    if timeout 1 bash -c "echo > /dev/tcp/127.0.0.1/$port" 2>/dev/null; then
        echo -e "${GREEN}🟢 :$port - $name${NC}"
        ((working++))
    else
        echo -e "${RED}🔴 :$port - $name${NC}"
    fi
done

echo ""
echo "📈 SUMMARY: $working/$total services running"

if [ $working -ge 6 ]; then
    echo -e "${GREEN}✅ SHADOWCORE OPERATIONAL${NC}"
    echo ""
    echo "🌐 ACCESS POINTS:"
    echo "  Dashboard:    http://$(curl -s ifconfig.me):8020"
    echo "  Main API:     http://$(curl -s ifconfig.me):8000"
    echo "  API Docs:     http://$(curl -s ifconfig.me):8000/docs"
    echo "  Proxy:        http://$(curl -s ifconfig.me):8080"
    echo "  Grafana:      http://$(curl -s ifconfig.me):3000"
else
    echo -e "${YELLOW}⚠️  Partial operation. Some services failed.${NC}"
    echo "Check logs in /opt/shadowcore/logs/"
fi

echo ""
echo "🔍 Quick test:"
curl -s http://127.0.0.1:8000/health 2>/dev/null | grep -q "healthy" && echo -e "${GREEN}✓ Main API healthy${NC}" || echo -e "${RED}✗ Main API down${NC}"
curl -s http://127.0.0.1:8020 2>/dev/null && echo -e "${GREEN}✓ Dashboard reachable${NC}" || echo -e "${RED}✗ Dashboard down${NC}"
curl -s http://127.0.0.1:8080 2>/dev/null && echo -e "${GREEN}✓ Proxy reachable${NC}" || echo -e "${RED}✗ Proxy down${NC}"
