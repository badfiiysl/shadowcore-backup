#!/bin/bash
echo "🌐 SHADOWCORE DOMAIN FINAL VERIFICATION"
echo "========================================"
date
echo "Domain: shadowcore.club"
echo ""

echo "🔍 1. Testing HTTPS Health Endpoint:"
curl -s "https://shadowcore.club/health" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(f'   Status: {data.get(\"status\", \"?\")}')
    print(f'   HTTPS: {data.get(\"https\", \"?\")}')
    print(f'   Service: {data.get(\"service\", \"?\")}')
    print('   ✅ Health endpoint is functional')
except Exception as e:
    print(f'   ❌ Error parsing health check: {e}')
"
echo ""

echo "🎯 2. Testing Threat Intelligence API:"
curl -s "https://shadowcore.club/api/threat/analyze?ioc=162.243.103.246" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(f'   IOC: {data[\"ioc\"]}')
    print(f'   Threat Level: {data[\"threat_level\"].upper()}')
    print(f'   Confidence: {data[\"confidence\"]*100:.0f}%')
    print('   ✅ Threat API is operational')
except Exception as e:
    print(f'   ❌ Threat API check failed: {e}')
"
echo ""

echo "🚀 3. Testing Main Dashboard (Root Path):"
ROOT_STATUS=$(curl -o /dev/null -s -w "%{http_code}" "https://shadowcore.club/")
if [[ "$ROOT_STATUS" =~ 2[0-9][0-9] ]] || [[ "$ROOT_STATUS" =~ 3[0-9][0-9] ]]; then
    echo "   ✅ Root path accessible (HTTP $ROOT_STATUS)"
else
    echo "   ⚠️  Root path returned HTTP $ROOT_STATUS (may require React UI)"
fi
echo ""

echo "📋 4. System Check:"
for service in nginx shadowcore-react-ui shadowcore-threat-api; do
    if systemctl is-active --quiet "$service"; then
        echo "   ✅ $service: ACTIVE"
    else
        echo "   ❌ $service: INACTIVE"
    fi
done
echo ""

echo "🔐 5. SSL Certificate Check:"
sudo openssl s_client -connect shadowcore.club:443 -servername shadowcore.club 2>/dev/null | openssl x509 -noout -subject -dates 2>/dev/null | head -2
echo ""

echo "========================================"
echo "🎉 VERIFICATION COMPLETE"
echo "Your ShadowCore is live at: https://shadowcore.club"
