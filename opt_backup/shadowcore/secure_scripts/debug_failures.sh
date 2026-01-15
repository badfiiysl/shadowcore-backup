#!/bin/bash
echo "🐛 Debugging Service Failures"
echo "============================="

# Check which processes are actually running
echo "1. Running processes:"
ps aux | grep -E "(python|node)" | grep -v grep | grep -i shadow

echo ""
echo "2. Checking logs..."
for log in /opt/shadowcore/logs/*.log; do
    if [ -f "$log" ]; then
        echo "=== $(basename $log) ==="
        tail -5 "$log"
        echo ""
    fi
done

echo ""
echo "3. Testing individual services..."

test_service() {
    local name="$1"
    local dir="$2"
    local cmd="$3"
    local port="$4"
    
    echo "🧪 Testing $name..."
    
    # Kill if already running
    pkill -f "$name" 2>/dev/null
    sleep 1
    
    # Start fresh
    echo "  Starting: cd $dir && $cmd"
    cd "$dir" && eval "nohup $cmd > /tmp/test_$name.log 2>&1 &"
    sleep 3
    
    # Check if running
    if ps aux | grep -q "$cmd"; then
        echo "  ✅ Process running"
    else
        echo "  ❌ Process died"
        echo "  Last error:"
        tail -3 "/tmp/test_$name.log"
    fi
    
    # Check port
    if timeout 1 bash -c "echo > /dev/tcp/127.0.0.1/$port" 2>/dev/null; then
        echo "  ✅ Port $port open"
    else
        echo "  ❌ Port $port closed"
    fi
    
    echo ""
}

# Test key services
test_service "Main REST API" "/opt/shadowcore/backend" "/opt/shadowcore/backend/venv/bin/python launch_rest.py --host 0.0.0.0 --port 8000" 8000
test_service "Auth API" "/opt/shadowcore/auth" "/opt/shadowcore/backend/venv/bin/python production_auth.py --host 127.0.0.1 --port 8006" 8006
test_service "WebSocket" "/opt/shadowcore/core" "/opt/shadowcore/backend/venv/bin/python websocket_production.py" 8083
test_service "Threat Insight" "/opt/shadowcore/threat-insight" "/opt/shadowcore/backend/venv/bin/python threat-insight-api.py" 9090
test_service "ShadowSearch" "/opt/shadowcore/shadowsearch" "node simple_8002.js" 8002
test_service "ShadowBrain" "/opt/shadowcore/shadowbrain" "node working-api.js" 8001
test_service "Electron" "/opt/shadowcore/electron" "node pure-server.js" 8082

echo ""
echo "4. Checking Python imports in virtual env..."
/opt/shadowcore/backend/venv/bin/python -c "
try:
    import flask
    print('✅ Flask:', flask.__version__)
except Exception as e:
    print('❌ Flask error:', str(e))

try:
    import psutil
    print('✅ psutil available')
except Exception as e:
    print('❌ psutil error:', str(e))
"
