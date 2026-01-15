#!/bin/bash
echo "🧹 Clean Migration to /opt"
echo "========================="

# Stop everything first
echo "Stopping services..."
pkill -f "python.*shadow" 2>/dev/null
pkill -f "node.*shadow" 2>/dev/null
sleep 2

# Clean /opt/shadowcore and start fresh
echo "Cleaning /opt/shadowcore..."
rm -rf /opt/shadowcore
mkdir -p /opt/shadowcore

# Find and copy ONLY the actual service files
echo "Looking for service files..."

# Python services we know about
PYTHON_SERVICES=(
    "launch_rest.py"
    "simple_threat_api.py"
    "simple_main_api.py"
    "production_auth.py"
    "real_proxy.py"
    "websocket_production.py"
    "dashboard.py"
    "threat-insight-api.py"
)

# Check what actually exists
echo "Available Python files:"
find /root/projects/shadowcore -name "*.py" -type f | grep -v "__pycache__" | grep -v ".cipd_bin" | grep -v "depot_tools" | grep -v "browser-build" | head -20

# Create directories
mkdir -p /opt/shadowcore/{backend,core,auth,ui,threat-insight,shadowsearch,shadowbrain,electron,logs}

# Copy known services
echo "Copying services..."
for service in "${PYTHON_SERVICES[@]}"; do
    find /root/projects/shadowcore -name "$service" -type f | head -1 | while read file; do
        if [ -f "$file" ]; then
            # Determine where to put it
            case "$service" in
                *launch*rest*|*simple_threat*|*simple_main*)
                    cp "$file" /opt/shadowcore/backend/
                    echo "✅ $service → backend/"
                    ;;
                *proxy*|*websocket*)
                    cp "$file" /opt/shadowcore/core/
                    echo "✅ $service → core/"
                    ;;
                *auth*)
                    cp "$file" /opt/shadowcore/auth/
                    echo "✅ $service → auth/"
                    ;;
                *dashboard*)
                    cp "$file" /opt/shadowcore/ui/
                    echo "✅ $service → ui/"
                    ;;
                *insight*)
                    cp "$file" /opt/shadowcore/threat-insight/
                    echo "✅ $service → threat-insight/"
                    ;;
                *)
                    cp "$file" /opt/shadowcore/
                    echo "✅ $service → root/"
                    ;;
            esac
        else
            echo "⚠️  $service not found"
        fi
    done
done

# Copy Node.js services
echo "Copying Node.js services..."
find /root/projects/shadowcore -name "simple_8002.js" -type f | head -1 | while read file; do
    cp "$file" /opt/shadowcore/shadowsearch/ 2>/dev/null && echo "✅ simple_8002.js → shadowsearch/"
done

find /root/projects/shadowcore -name "working-api.js" -type f | head -1 | while read file; do
    cp "$file" /opt/shadowcore/shadowbrain/ 2>/dev/null && echo "✅ working-api.js → shadowbrain/"
done

# Copy electron if exists
if [ -f "/root/shadowcore-electron/pure-server.js" ]; then
    cp "/root/shadowcore-electron/pure-server.js" /opt/shadowcore/electron/
    echo "✅ pure-server.js → electron/"
fi

# Create virtual environment
echo "Setting up Python environment..."
cd /opt/shadowcore/backend
python3 -m venv venv
source venv/bin/activate
venv/bin/pip install flask fastapi psutil requests > /opt/shadowcore/logs/install.log 2>&1

# Create simple start script
echo "Creating startup script..."
cat > /opt/shadowcore/start.sh << 'START'
#!/bin/bash
cd /opt/shadowcore

echo "🚀 Starting ShadowCore..."

# Start Python services
cd backend && venv/bin/python launch_rest.py --host 0.0.0.0 --port 8000 > ../logs/main_api.log 2>&1 &
cd backend && venv/bin/python simple_threat_api.py --host 127.0.0.1 --port 8003 > ../logs/threat_api.log 2>&1 &
cd backend && venv/bin/python simple_main_api.py --host 127.0.0.1 --port 8004 > ../logs/main_api2.log 2>&1 &
cd auth && ../backend/venv/bin/python production_auth.py --host 127.0.0.1 --port 8006 > ../logs/auth.log 2>&1 &
cd core && ../backend/venv/bin/python real_proxy.py > ../logs/proxy.log 2>&1 &
cd core && ../backend/venv/bin/python websocket_production.py > ../logs/websocket.log 2>&1 &
cd ui && ../backend/venv/bin/python dashboard.py > ../logs/dashboard.log 2>&1 &
cd threat-insight && ../backend/venv/bin/python threat-insight-api.py > ../logs/insight.log 2>&1 &

# Start Node.js services
cd shadowsearch && node simple_8002.js > ../logs/search.log 2>&1 &
cd shadowbrain && node working-api.js > ../logs/brain.log 2>&1 &
cd electron && node pure-server.js > ../logs/electron.log 2>&1 &

echo "✅ Services started!"
echo "📊 Check logs: ls -la /opt/shadowcore/logs/"
echo "🔍 Check ports: netstat -tulpn | grep -E '8000|8001|8002|8003|8004|8006|8080|8082|8083|8020|9090'"
START

chmod +x /opt/shadowcore/start.sh

# Create health check
cat > /opt/shadowcore/health.sh << 'HEALTH'
#!/bin/bash
echo "🩺 ShadowCore Health Check"
ports=(8000 8003 8004 8006 8080 8083 8020 9090 8002 8001 8082)
for port in "${ports[@]}"; do
    if timeout 1 bash -c "echo > /dev/tcp/127.0.0.1/$port" 2>/dev/null; then
        echo "🟢 Port $port: OPEN"
    else
        echo "🔴 Port $port: CLOSED"
    fi
done
HEALTH

chmod +x /opt/shadowcore/health.sh

echo ""
echo "✅ Migration complete!"
echo "👉 Run: /opt/shadowcore/start.sh"
echo "👉 Check: /opt/shadowcore/health.sh"
echo ""
echo "📁 Structure:"
tree /opt/shadowcore -L 2
