#!/bin/bash
echo "🚀 Migrating ShadowCore to /opt"
echo "================================"

SRC="/root/projects/shadowcore"
DEST="/opt/shadowcore"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# Step 1: Check source
if [ ! -d "$SRC" ]; then
    error "Source directory not found: $SRC"
    exit 1
fi

log "Source: $SRC"
log "Destination: $DEST"

# Step 2: Create proper structure in /opt
log "Creating directory structure..."
mkdir -p $DEST/{backend,core,auth,ui,threat-insight,shadowsearch,shadowbrain,logs,config}

# Step 3: Copy files to correct locations
log "Copying Python services..."

# Backend services
cp $SRC/launch_rest.py $DEST/backend/ 2>/dev/null && log "✅ launch_rest.py" || warning "launch_rest.py not found"
cp $SRC/simple_threat_api.py $DEST/backend/ 2>/dev/null && log "✅ simple_threat_api.py" || warning "simple_threat_api.py not found"
cp $SRC/simple_main_api.py $DEST/backend/ 2>/dev/null && log "✅ simple_main_api.py" || warning "simple_main_api.py not found"

# Find and copy rpc server
find $SRC -name "server.py" -path "*rpc*" -exec cp {} $DEST/backend/ 2>/dev/null \; && log "✅ rpc/server.py" || warning "rpc/server.py not found"

# Core services
cp $SRC/real_proxy.py $DEST/core/ 2>/dev/null && log "✅ real_proxy.py" || warning "real_proxy.py not found"
cp $SRC/websocket_production.py $DEST/core/ 2>/dev/null && log "✅ websocket_production.py" || warning "websocket_production.py not found"

# Auth service
cp $SRC/production_auth.py $DEST/auth/ 2>/dev/null && log "✅ production_auth.py" || warning "production_auth.py not found"

# UI service
cp $SRC/dashboard.py $DEST/ui/ 2>/dev/null && log "✅ dashboard.py" || warning "dashboard.py not found"

# Threat insight
cp $SRC/threat-insight-api.py $DEST/threat-insight/ 2>/dev/null && log "✅ threat-insight-api.py" || warning "threat-insight-api.py not found"

# Node.js services
log "Copying Node.js services..."
cp $SRC/simple_8002.js $DEST/shadowsearch/ 2>/dev/null && log "✅ simple_8002.js" || warning "simple_8002.js not found"
cp $SRC/working-api.js $DEST/shadowbrain/ 2>/dev/null && log "✅ working-api.js" || warning "working-api.js not found"

# Copy electron server from /root/shadowcore-electron
if [ -f "/root/shadowcore-electron/pure-server.js" ]; then
    mkdir -p $DEST/electron
    cp /root/shadowcore-electron/pure-server.js $DEST/electron/
    log "✅ electron/pure-server.js"
fi

# Step 4: Copy any requirements.txt
if [ -f "$SRC/requirements.txt" ]; then
    cp $SRC/requirements.txt $DEST/backend/
    log "✅ requirements.txt"
fi

# Step 5: Create virtual environment
log "Setting up Python virtual environment..."
cd $DEST/backend
python3 -m venv venv
source venv/bin/activate

# Install common dependencies
log "Installing dependencies..."
venv/bin/pip install flask fastapi psutil requests python-socketio eventlet > $DEST/logs/install.log 2>&1

# Install from requirements.txt if exists
if [ -f "requirements.txt" ]; then
    venv/bin/pip install -r requirements.txt >> $DEST/logs/install.log 2>&1
fi

# Step 6: Create startup script
log "Creating startup scripts..."

# Main startup script
cat > $DEST/start.sh << 'STARTEOF'
#!/bin/bash
echo "🚀 Starting ShadowCore..."
cd /opt/shadowcore

# Python services
cd backend && nohup venv/bin/python launch_rest.py --host 0.0.0.0 --port 8000 > ../logs/main_api.log 2>&1 &
cd backend && nohup venv/bin/python simple_threat_api.py --host 127.0.0.1 --port 8003 > ../logs/threat_api.log 2>&1 &
cd backend && nohup venv/bin/python simple_main_api.py --host 127.0.0.1 --port 8004 > ../logs/main_api2.log 2>&1 &
cd auth && nohup ../backend/venv/bin/python production_auth.py --host 127.0.0.1 --port 8006 > ../logs/auth.log 2>&1 &
cd core && nohup ../backend/venv/bin/python real_proxy.py > ../logs/proxy.log 2>&1 &
cd core && nohup ../backend/venv/bin/python websocket_production.py > ../logs/websocket.log 2>&1 &
cd backend && nohup venv/bin/python -c "import sys; sys.path.append('.'); from rpc import server; server.run()" > ../logs/rpc.log 2>&1 &
cd ui && nohup ../backend/venv/bin/python dashboard.py > ../logs/dashboard.log 2>&1 &
cd threat-insight && nohup ../backend/venv/bin/python threat-insight-api.py > ../logs/insight.log 2>&1 &

# Node.js services
cd shadowsearch && nohup node simple_8002.js > ../logs/search.log 2>&1 &
cd shadowbrain && nohup node working-api.js > ../logs/brain.log 2>&1 &
cd electron && nohup node pure-server.js > ../logs/electron.log 2>&1 &

echo "✅ ShadowCore services started!"
echo "📊 Check logs: /opt/shadowcore/logs/"
echo "🔍 Check ports: netstat -tulpn | grep -E '8000|8001|8002|8003|8004|8006|8080|8082|8083|8020|9090|4242'"
STARTEOF

chmod +x $DEST/start.sh

# Health check script
cat > $DEST/health.sh << 'HEALTHEOF'
#!/bin/bash
echo "🩺 ShadowCore Health Check"
echo "=========================="

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

for entry in "${ports[@]}"; do
    port="${entry%%:*}"
    name="${entry#*:}"
    if timeout 1 bash -c "echo > /dev/tcp/127.0.0.1/$port" 2>/dev/null; then
        echo "🟢 :$port - $name"
    else
        echo "🔴 :$port - $name"
    fi
done

echo ""
echo "📊 Process count:"
ps aux | grep -E "(python.*shadow|node.*shadow)" | grep -v grep | wc -l
HEALTHEOF

chmod +x $DEST/health.sh

# Stop script
cat > $DEST/stop.sh << 'STOPEOF'
#!/bin/bash
echo "🛑 Stopping ShadowCore..."
pkill -f "python.*shadowcore"
pkill -f "node.*shadow"
sleep 2
echo "✅ Stopped"
STOPEOF

chmod +x $DEST/stop.sh

# Step 7: Set permissions
log "Setting permissions..."
chown -R root:root $DEST
find $DEST -type f -name "*.py" -exec chmod +x {} \;
find $DEST -type f -name "*.js" -exec chmod +x {} \;
find $DEST -type f -name "*.sh" -exec chmod +x {} \;

# Step 8: Create systemd service
log "Creating systemd service..."
cat > /tmp/shadowcore.service << 'SVC'
[Unit]
Description=ShadowCore Security Platform
After=network.target postgresql.service redis.service neo4j.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/opt/shadowcore/start.sh
ExecStop=/opt/shadowcore/stop.sh
WorkingDirectory=/opt/shadowcore
User=root
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
SVC

echo "Systemd service file created at /tmp/shadowcore.service"
echo "To enable: sudo cp /tmp/shadowcore.service /etc/systemd/system/ && sudo systemctl enable shadowcore"

# Step 9: Summary
log "✅ Migration complete!"
echo ""
echo "📁 New structure:"
tree $DEST -L 2
echo ""
echo "🚀 To start: /opt/shadowcore/start.sh"
echo "🩺 Health check: /opt/shadowcore/health.sh"
echo "🛑 Stop: /opt/shadowcore/stop.sh"
echo ""
echo "Next steps:"
echo "1. sudo cp /tmp/shadowcore.service /etc/systemd/system/"
echo "2. sudo systemctl daemon-reload"
echo "3. sudo systemctl enable shadowcore"
echo "4. sudo systemctl start shadowcore"
