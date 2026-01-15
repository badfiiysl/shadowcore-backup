#!/bin/bash
# ShadowCore Startup Script
# Run: bash shadowcore_start.sh [service]

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

check_port() {
    nc -z -w2 $1 $2 > /dev/null 2>&1
    return $?
}

start_python_service() {
    local name=$1
    local script=$2
    local port=$3
    
    if check_port "127.0.0.1" "$port"; then
        warning "$name (port $port) is already running"
        return 0
    fi
    
    if [ ! -f "$script" ]; then
        error "Script not found: $script"
        return 1
    fi
    
    log "Starting $name on port $port..."
    nohup python3 "$script" > "/tmp/${name}.log" 2>&1 &
    echo $! > "/tmp/${name}.pid"
    
    sleep 2
    if check_port "127.0.0.1" "$port"; then
        log "✓ $name started successfully (PID: $(cat /tmp/${name}.pid))"
    else
        error "Failed to start $name"
        return 1
    fi
}

start_node_service() {
    local name=$1
    local script=$2
    local port=$3
    
    if check_port "127.0.0.1" "$port"; then
        warning "$name (port $port) is already running"
        return 0
    fi
    
    if [ ! -f "$script" ]; then
        error "Script not found: $script"
        return 1
    fi
    
    log "Starting $name on port $port..."
    nohup node "$script" > "/tmp/${name}.log" 2>&1 &
    echo $! > "/tmp/${name}.pid"
    
    sleep 2
    if check_port "127.0.0.1" "$port"; then
        log "✓ $name started successfully (PID: $(cat /tmp/${name}.pid))"
    else
        error "Failed to start $name"
        return 1
    fi
}

start_infra() {
    log "Checking infrastructure services..."
    
    # Check PostgreSQL
    if ! check_port "127.0.0.1" 5432; then
        warning "PostgreSQL (5432) not running - start manually: sudo systemctl start postgresql"
    else
        log "✓ PostgreSQL is running"
    fi
    
    # Check Redis
    if ! check_port "127.0.0.1" 6379; then
        warning "Redis (6379) not running - start manually: sudo systemctl start redis"
    else
        log "✓ Redis is running"
    fi
    
    # Check Neo4j
    if ! check_port "127.0.0.1" 7474; then
        warning "Neo4j (7474) not running - start manually: sudo systemctl start neo4j"
    else
        log "✓ Neo4j is running"
    fi
}

start_all() {
    echo "🚀 Starting ShadowCore Stack..."
    echo "========================================"
    
    # Infrastructure first
    start_infra
    
    # Python Services
    start_python_service "main_rest" "/opt/shadowcore-backend/launch_rest.py --host 0.0.0.0 --port 8000" 8000
    start_python_service "threat_api" "/opt/shadowcore-backend/simple_threat_api.py --host 127.0.0.1 --port 8003" 8003
    start_python_service "main_api" "/opt/shadowcore-backend/simple_main_api.py --host 127.0.0.1 --port 8004" 8004
    start_python_service "auth_api" "/opt/shadowcore-auth/production_auth.py --host 127.0.0.1 --port 8006" 8006
    start_python_service "proxy" "/opt/shadowcore/real_proxy.py" 8080
    start_python_service "websocket" "/opt/shadowcore/websocket_production.py" 8083
    start_python_service "rpc" "/opt/shadowcore-backend/rpc/server.py" 4242
    start_python_service "ui_dashboard" "/opt/shadowcore/ui/dashboard.py" 8020
    start_python_service "threat_insight" "/opt/threat-insight/threat-insight-api.py" 9090
    
    # Node.js Services
    start_node_service "shadowsearch" "/opt/shadowsearch/simple_8002.js" 8002
    start_node_service "shadowbrain" "/opt/shadowbrain/working-api.js" 8001
    start_node_service "electron" "/root/shadowcore-electron/pure-server.js" 8082
    
    echo "========================================"
    log "All services started! Checking health..."
    
    # Quick health check
    sleep 3
    echo ""
    log "Running health check..."
    python3 /tmp/shadowcore_health.py
}

stop_all() {
    log "Stopping all ShadowCore services..."
    
    for pidfile in /tmp/*.pid; do
        if [ -f "$pidfile" ]; then
            pid=$(cat "$pidfile")
            service=$(basename "$pidfile" .pid)
            log "Stopping $service (PID: $pid)..."
            kill $pid 2>/dev/null
            rm -f "$pidfile"
        fi
    done
    
    log "All services stopped"
}

status_all() {
    log "ShadowCore Service Status"
    echo "========================================"
    
    # Check Python services
    services=(
        "8000:Main REST API"
        "8003:Threat API" 
        "8004:Main API"
        "8006:Auth API"
        "8080:Proxy"
        "8083:WebSocket"
        "4242:RPC Server"
        "8020:UI Dashboard"
        "9090:Threat Insight"
    )
    
    for service in "${services[@]}"; do
        port="${service%%:*}"
        name="${service#*:}"
        if check_port "127.0.0.1" "$port"; then
            echo -e "${GREEN}✓${NC} $name (port $port) is UP"
        else
            echo -e "${RED}✗${NC} $name (port $port) is DOWN"
        fi
    done
}

case "${1:-all}" in
    all)
        start_all
        ;;
    stop)
        stop_all
        ;;
    status)
        status_all
        ;;
    health)
        python3 /tmp/shadowcore_health.py --all
        ;;
    *)
        echo "Usage: $0 {all|stop|status|health}"
        exit 1
        ;;
esac
