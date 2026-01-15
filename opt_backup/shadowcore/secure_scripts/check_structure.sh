#!/bin/bash
echo "📁 Checking ShadowCore Structure"
echo "================================"

BASE="/root/projects/shadowcore"
if [ ! -d "$BASE" ]; then
    echo "❌ Base directory not found: $BASE"
    echo "Available in /root/projects/:"
    ls -la /root/projects/ 2>/dev/null
    exit 1
fi

echo "✅ Base directory: $BASE"
echo ""

echo "Directory structure:"
find "$BASE" -type f -name "*.py" -o -name "*.js" | grep -v "__pycache__" | grep -v "node_modules" | sort | head -30

echo ""
echo "🔍 Key files check:"
check_file() {
    if [ -f "$1" ]; then
        echo "✅ $1"
    else
        echo "❌ $1 (MISSING)"
    fi
}

check_file "$BASE/backend/launch_rest.py"
check_file "$BASE/backend/simple_threat_api.py"
check_file "$BASE/backend/simple_main_api.py"
check_file "$BASE/backend/rpc/server.py"
check_file "$BASE/core/real_proxy.py"
check_file "$BASE/core/websocket_production.py"
check_file "$BASE/auth/production_auth.py"
check_file "$BASE/ui/dashboard.py"
check_file "$BASE/threat-insight/threat-insight-api.py"
check_file "$BASE/shadowsearch/simple_8002.js"
check_file "$BASE/shadowbrain/working-api.js"

echo ""
echo "🐍 Python virtual environment:"
if [ -f "$BASE/backend/venv/bin/python" ]; then
    echo "✅ Virtual env exists"
    $BASE/backend/venv/bin/python --version
else
    echo "❌ Virtual env missing"
    echo "Creating one..."
    cd "$BASE/backend" && python3 -m venv venv
fi

echo ""
echo "📦 Python dependencies check:"
if [ -f "$BASE/backend/requirements.txt" ]; then
    echo "✅ requirements.txt exists"
    echo "Installing dependencies..."
    "$BASE/backend/venv/bin/pip" install -r "$BASE/backend/requirements.txt" 2>/dev/null | tail -5
else
    echo "⚠️  No requirements.txt found"
fi
