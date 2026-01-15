#!/bin/bash
echo "🚀 ShadowCore Full Recovery"
echo "==========================="

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# Step 1: Stop everything properly
log "Step 1: Stopping all ShadowCore services..."

# Check for systemd services
echo "Checking systemd services..."
systemctl list-unit-files | grep -i shadow | while read line; do
    svc=$(echo $line | awk '{print $1}')
    if systemctl is-active --quiet $svc; then
        log "Stopping systemd service: $svc"
        sudo systemctl stop $svc
    fi
done

# Kill remaining processes
log "Killing remaining processes..."
pkill -9 -f "python.*shadow" 2>/dev/null
pkill -9 -f "node.*shadow" 2>/dev/null
pkill -9 -f "shadowcore" 2>/dev/null

# Kill by port
for port in 8000 8001 8002 8003 8004 8006 8080 8082 8083 8020 9090 4242; do
    fuser -k $port/tcp 2>/dev/null
done

sleep 3

# Step 2: Start infrastructure
log "Step 2: Starting infrastructure..."
infra_services=("postgresql" "redis" "neo4j" "docker" "containerd")
for svc in "${infra_services[@]}"; do
    if systemctl is-enabled $svc 2>/dev/null; then
        if ! systemctl is-active --quiet $svc; then
            log "Starting $svc..."
            sudo systemctl start $svc
        else
            log "$svc is already running"
        fi
    fi
done

sleep 2

# Step 3: Start Python services with proper logging
log "Step 3: Starting Python services..."

start_python_service() {
    local name="$1"
    local cmd="$2"
    local log_file="/var/log/shadowcore/${name// /_}.log"
    
    mkdir -p /var/log/shadowcore
    log "Starting $name..."
    echo "Command: $cmd" >> "$log_file"
    echo "Started at: $(date)" >> "$log_file"
    
    # Run in background with nohup and proper redirection
    nohup bash -c "$cmd" >> "$log_file" 2>&1 &
    local pid=$!
    
    echo $pid > "/tmp/shadowcore_${name// /_}.pid"
    log "Started $name (PID: $pid)"
    return $pid
}

# Define all Python services
python_services=(
    "Main REST API|cd /opt/shadowcore-backend && /opt/shadowcore-backend/venv/bin/python launch_rest.py --host 0.0.0.0 --port 8000"
    "Threat API|cd /opt/shadowcore-backend && python3 simple_threat_api.py --host 127.0.0.1 --port 8003"
    "Main API|cd /opt/shadowcore-backend && python3 simple_main_api.py --host 127.0.0.1 --port 8004"
    "Auth API|cd /opt/shadowcore-auth && python3 production_auth.py --host 127.0.0.1 --port 8006"
    "Proxy|cd /opt/shadowcore && python3 real_proxy.py"
    "WebSocket|cd /opt/shadowcore && python3 websocket_production.py"
    "RPC Server|cd /opt/shadowcore-backend && /opt/shadowcore-backend/venv/bin/python rpc/server.py"
    "UI Dashboard|cd /opt/shadowcore/ui && python3 dashboard.py"
    "Threat Insight|cd /opt/threat-insight && python3 threat-insight-api.py"
)

for service in "${python_services[@]}"; do
    IFS='|' read -r name cmd <<< "$service"
    start_python_service "$name" "$cmd"
    sleep 1
done

# Step 4: Start Node.js services
log "Step 4: Starting Node.js services..."

start_node_service() {
    local name="$1"
    local cmd="$2"
    local log_file="/var/log/shadowcore/${name// /_}.log"
    
    log "Starting $name..."
    echo "Command: $cmd" >> "$log_file"
    echo "Started at: $(date)" >> "$log_file"
    
    nohup bash -c "$cmd" >> "$log_file" 2>&1 &
    local pid=$!
    
    echo $pid > "/tmp/shadowcore_${name// /_}.pid"
    log "Started $name (PID: $pid)"
}

node_services=(
    "ShadowSearch|cd /opt/shadowsearch && node simple_8002.js"
    "ShadowBrain API|cd /opt/shadowbrain && node working-api.js"
    "Electron Server|cd /root/shadowcore-electron && node pure-server.js"
)

for service in "${node_services[@]}"; do
    IFS='|' read -r name cmd <<< "$service"
    start_node_service "$name" "$cmd"
    sleep 1
done

# Step 5: Wait and verify
log "Step 5: Waiting for services to start..."
sleep 5

# Step 6: Health check
log "Step 6: Running health check..."
bash /tmp/simple_working_check.sh

# Step 7: Create startup script for future
log "Step 7: Creating auto-start script..."

cat > /usr/local/bin/start-shadowcore << 'EOF'
#!/bin/bash
# Auto-start ShadowCore
echo "Starting ShadowCore..."
cd /opt/shadowcore-backend && /opt/shadowcore-backend/venv/bin/python launch_rest.py --host 0.0.0.0 --port 8000 &
cd /opt/shadowcore-backend && python3 simple_threat_api.py --host 127.0.0.1 --port 8003 &
cd /opt/shadowcore-backend && python3 simple_main_api.py --host 127.0.0.1 --port 8004 &
cd /opt/shadowcore-auth && python3 production_auth.py --host 127.0.0.1 --port 8006 &
cd /opt/shadowcore && python3 real_proxy.py &
cd /opt/shadowcore && python3 websocket_production.py &
cd /opt/shadowcore-backend && /opt/shadowcore-backend/venv/bin/python rpc/server.py &
cd /opt/shadowcore/ui && python3 dashboard.py &
cd /opt/threat-insight && python3 threat-insight-api.py &
cd /opt/shadowsearch && node simple_8002.js &
cd /opt/shadowbrain && node working-api.js &
cd /root/shadowcore-electron && node pure-server.js &
echo "ShadowCore started!"
