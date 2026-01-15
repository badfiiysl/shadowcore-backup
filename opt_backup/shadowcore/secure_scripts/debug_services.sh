#!/bin/bash
echo "🐛 ShadowCore Debug Script"
echo "=========================="

echo "1. Checking Python environment..."
python3 --version
which python3

echo -e "\n2. Checking Node.js environment..."
node --version
which node

echo -e "\n3. Checking if directories exist..."
for dir in /opt/shadowcore-backend /opt/shadowcore /opt/shadowcore-auth /opt/shadowcore/ui /opt/threat-insight /opt/shadowsearch /opt/shadowbrain /root/shadowcore-electron; do
    if [ -d "$dir" ]; then
        echo "✅ $dir"
        ls -la "$dir/"*.py "$dir/"*.js 2>/dev/null | head -2
    else
        echo "❌ $dir (MISSING)"
    fi
done

echo -e "\n4. Checking Python virtual environment..."
if [ -f "/opt/shadowcore-backend/venv/bin/python" ]; then
    echo "✅ Virtual env exists"
    /opt/shadowcore-backend/venv/bin/python --version
else
    echo "❌ Virtual env missing"
fi

echo -e "\n5. Checking recent process failures..."
ps aux | grep -E "(python|node)" | grep -v grep | head -5

echo -e "\n6. Checking recent logs..."
for log in /var/log/shadowcore/*.log /tmp/*.log 2>/dev/null; do
    echo "=== $(basename $log) ==="
    tail -5 "$log" 2>/dev/null | sed 's/^/  /'
done

echo -e "\n7. Testing Python imports..."
cat > /tmp/test_imports.py << 'PYEOF'
import sys
print("Python path:", sys.executable)
print("Python version:", sys.version)

try:
    import flask
    print("✅ Flask:", flask.__version__)
except ImportError as e:
    print("❌ Flask:", e)

try:
    import fastapi
    print("✅ FastAPI available")
except ImportError as e:
    print("❌ FastAPI:", e)

try:
    import psutil
    print("✅ psutil available")
except ImportError as e:
    print("❌ psutil:", e)
PYEOF
python3 /tmp/test_imports.py

echo -e "\n8. Trying to start a simple test service..."
cat > /tmp/test_server.py << 'PYEOF'
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Test OK'

@app.route('/health')
def health():
    return {'status': 'ok'}

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9999)
PYEOF

echo "Starting test server on port 9999..."
timeout 2 python3 /tmp/test_server.py > /tmp/test_server.log 2>&1 &
sleep 2

if curl -s http://127.0.0.1:9999/health > /dev/null; then
    echo "✅ Test server works"
    pkill -f "test_server.py"
else
    echo "❌ Test server failed"
    cat /tmp/test_server.log
fi
