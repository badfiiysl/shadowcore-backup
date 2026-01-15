#!/bin/bash
echo "🚀 Starting ShadowCore from /root/projects/shadowcore"
echo "===================================================="

BASE_DIR="/root/projects/shadowcore"
VENV_PATH="$BASE_DIR/backend/venv/bin/python"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# Check if base directory exists
if [ ! -d "$BASE_DIR" ]; then
    error "Base directory not found: $BASE_DIR"
    echo "Available directories in /root/projects/:"
    ls -la /root/projects/ 2>/dev/null || echo "No /root/projects directory"
    exit 1
fi

log "Base directory: $BASE_DIR"
ls -la "$BASE_DIR/"

# Check virtual environment
if [ ! -f "$VENV_PATH" ]; then
    warning "Virtual environment not found at $VENV_PATH"
    warning "Trying system Python instead..."
    PYTHON_CMD="python3"
else
    PYTHON_CMD="$VENV_PATH"
    log "Using virtual environment: $VENV_PATH"
fi

# Function to start service
start_service() {
    local name="$1"
    local dir="$2"
    local cmd="$3"
    local port="$4"
    
    log "Starting $name..."
    
    # Check if port is already in use
    if timeout 1 bash -c "echo > /dev/tcp/127.0.0.1/$port" 2>/dev/null; then
        warning "$name (port $port) is already running"
        return 0
    fi
    
    # Create log directory
    mkdir -p /var/log/shadowcore
    
    # Change to directory and run command
    if [ -d "$dir" ]; then
        cd "$dir"
        nohup $cmd > "/var/log/shadowcore/${name// /_}.log" 2>&1 &
        local pid=$!
        sleep 2
        
        if ps -p $pid > /dev/null 2>&1; then
            log "✅ $name started (PID: $pid)"
            echo $pid > "/tmp/shadowcore_${name// /_}.pid"
        else
            error "Failed to start $name"
            echo "Last 3 lines of log:"
            tail -3 "/var/log/shadowcore/${name// /_}.log" 2>/dev/null
        fi
    else
        error "Directory not found: $dir"
    fi
}

# Stop any running shadowcore processes first
log "Stopping any existing shadowcore processes..."
pkill -f "python.*shadow" 2>/dev/null
pkill -f "node.*shadow" 2>/dev/null
sleep 2

# Start services in correct order
log "Starting services..."

# 1. Backend services
start_service "Main REST API" "$BASE_DIR/backend" "$PYTHON_CMD launch_rest.py --host 0.0.0.0 --port 8000" 8000
sleep 2

start_service "Threat API" "$BASE_DIR/backend" "$PYTHON_CMD simple_threat_api.py --host 127.0.0.1 --port 8003" 8003
sleep 2

start_service "Main API" "$BASE_DIR/backend" "$PYTHON_CMD simple_main_api.py --host 127.0.0.1 --port 8004" 8004
sleep 2

# 2. Auth service
if [ -d "$BASE_DIR/auth" ]; then
    start_service "Auth API" "$BASE_DIR/auth" "$PYTHON_CMD production_auth.py --host 127.0.0.1 --port 8006" 8006
    sleep 2
else
    warning "Auth directory not found, skipping Auth API"
fi

# 3. Core services
start_service "Proxy" "$BASE_DIR/core" "$PYTHON_CMD real_proxy.py" 8080
sleep 2

start_service "WebSocket" "$BASE_DIR/core" "$PYTHON_CMD websocket_production.py" 8083
sleep 2

# 4. RPC service
start_service "RPC Server" "$BASE_DIR/backend/rpc" "$PYTHON_CMD server.py" 4242
sleep 2

# 5. UI Dashboard
if [ -d "$BASE_DIR/ui" ]; then
    start_service "UI Dashboard" "$BASE_DIR/ui" "$PYTHON_CMD dashboard.py" 8020
    sleep 2
else
    warning "UI directory not found, skipping UI Dashboard"
fi

# 6. Threat Insight
if [ -d "$BASE_DIR/threat-insight" ]; then
    start_service "Threat Insight" "$BASE_DIR/threat-insight" "$PYTHON_CMD threat-insight-api.py" 9090
    sleep 2
else
    warning "Threat Insight directory not found"
fi

# 7. Node.js services
# ShadowSearch
if [ -f "$BASE_DIR/shadowsearch/simple_8002.js" ]; then
    start_service "ShadowSearch" "$BASE_DIR/shadowsearch" "node simple_8002.js" 8002
    sleep 2
fi

# ShadowBrain
if [ -f "$BASE_DIR/shadowbrain/working-api.js" ]; then
    start_service "ShadowBrain API" "$BASE_DIR/shadowbrain" "node working-api.js" 8001
    sleep 2
fi

# Electron Server
if [ -f "/root/shadowcore-electron/pure-server.js" ]; then
    start_service "Electron Server" "/root/shadowcore-electron" "node pure-server.js" 8082
    sleep 2
fi

# Health check
log "Running health check..."
echo ""
echo "📊 PORT STATUS:"
echo "--------------"

ports=(
    "8000:Main REST API"
    "8003:Threat API"
    "8004:Main API"
    "8006:Auth API"
    "8080:Proxy"
    "8083:WebSocket"
    "4242:RPC Server"
    "8020:UI Dashboard"
    "9090:Threat Insight"
    "8002:ShadowSearch"
    "8001:ShadowBrain API"
    "8082:Electron Server"
)

all_ok=true
for entry in "${ports[@]}"; do
    port="${entry%%:*}"
    name="${entry#*:}"
    
    if timeout 1 bash -c "echo > /dev/tcp/127.0.0.1/$port" 2>/dev/null; then
        echo -e "${GREEN}🟢${NC} :$port - $name"
    else
        echo -e "${RED}🔴${NC} :$port - $name"
        all_ok=false
    fi
done

echo ""
if $all_ok; then
    log "✅ All services started successfully!"
else
    warning "Some services failed to start. Check logs in /var/log/shadowcore/"
fi

echo ""
log "📋 Running processes:"
ps aux | grep -E "(python|node)" | grep -i shadow | grep -v grep | awk '{printf "  PID %-8s %s\n", $2, $11" "$12" "$13}'

echo ""
log "🚀 Quick test commands:"
echo "  curl http://127.0.0.1:8000"
echo "  curl http://127.0.0.1:8020"
echo "  tail -f /var/log/shadowcore/*.log"
