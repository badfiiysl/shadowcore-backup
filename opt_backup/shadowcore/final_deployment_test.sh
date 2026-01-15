#!/bin/bash
echo "🏆 FINAL SHADOWCORE DEPLOYMENT TEST"
echo "=================================="

echo -e "\n🎯 BACKEND CONNECTIVITY:"
# Test each backend service
test_endpoint() {
    local name=$1
    local url=$2
    local expected=$3
    
    if curl -s -o /dev/null -w "%{http_code}" $url | grep -q "$expected"; then
        echo "✅ $name: HTTP $expected OK"
        return 0
    else
        echo "❌ $name: Failed to reach $url"
        return 1
    fi
}

test_endpoint "Threat API" "http://localhost:8003/health" "200"
test_endpoint "Dashboard" "http://localhost:8020" "200"
test_endpoint "React UI" "http://localhost:3002" "200"
test_endpoint "Grafana" "http://localhost:3000" "200|302|401"

echo -e "\n🎯 THREAT DETECTION (Live Test):"
curl -s "http://localhost:8003/analyze?ioc=162.243.103.246" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(f'✅ Threat Analysis: {data[\"ioc\"]} → {data[\"threat_level\"].upper()}')
    print(f'   Confidence: {data[\"confidence\"]*100:.0f}%')
except:
    print('❌ Threat API failed')
"

echo -e "\n🌐 NGINX PROXY TEST:"
# Test through Nginx proxy
if curl -s "http://localhost/health" > /dev/null; then
    echo "✅ Nginx health endpoint accessible"
else
    echo "❌ Nginx not responding on /health"
fi

echo -e "\n📊 SYSTEM RESOURCES:"
echo "Memory usage:"
free -h | head -2
echo -e "\nDisk usage:"
df -h / | tail -1

echo -e "\n=================================="
echo "🚀 DEPLOYMENT TEST COMPLETE"
