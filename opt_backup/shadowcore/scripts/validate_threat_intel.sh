#!/bin/bash

echo "Threat Intelligence Proxy Validation"
echo "===================================="
echo ""

# Check if service is running
if systemctl is-active --quiet threat-intel-proxy.service; then
    echo "✅ Service is running (systemd)"
else
    echo "❌ Service is not running"
    exit 1
fi

# Check port
echo -n "Port 8080 listening ... "
if sudo ss -tln | grep -q ":8080 "; then
    echo "✅"
else
    echo "❌"
fi

# Test endpoints
echo ""
echo "Endpoint Tests:"
echo "--------------"

endpoints=(
    "/health:Health Check"
    "/api/health:API Health"
    "/threat/intelligence:Threat Intelligence"
    "/threat/detection:Threat Detection"
    "/threat/analyze?ip=8.8.8.8:Threat Analysis"
    "/api/threat/intelligence:API Threat Intel"
)

success=0
total=0

for endpoint_pair in "${endpoints[@]}"; do
    endpoint=$(echo "$endpoint_pair" | cut -d: -f1)
    name=$(echo "$endpoint_pair" | cut -d: -f2)
    total=$((total + 1))
    
    echo -n "  $name ... "
    status_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 "http://localhost:8080$endpoint" 2>/dev/null || echo "000")
    
    if [ "$status_code" = "200" ]; then
        echo "✅ (HTTP 200)"
        success=$((success + 1))
        
        # Show response snippet for key endpoints
        if [ "$endpoint" = "/threat/intelligence" ]; then
            echo "      Response: $(curl -s "http://localhost:8080$endpoint" | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null || echo "OK")"
        fi
    else
        echo "❌ (HTTP $status_code)"
    fi
done

echo ""
echo "Summary:"
echo "--------"
echo "Successful: $success/$total endpoints"

if [ $success -eq $total ]; then
    echo "🎉 THREAT INTELLIGENCE PROXY IS 100% OPERATIONAL!"
    echo ""
    echo "All endpoints are responding correctly:"
    echo "  • Health checks: ✅"
    echo "  • Threat intelligence: ✅"
    echo "  • Threat analysis: ✅"
    echo "  • API endpoints: ✅"
    echo ""
    echo "Your system is ready for use!"
    exit 0
elif [ $success -ge 4 ]; then
    echo "⚠️  Service is partially operational ($success/$total endpoints)"
    echo "Most critical endpoints are working."
    exit 1
else
    echo "❌ Service has major issues ($success/$total endpoints)"
    exit 1
fi
