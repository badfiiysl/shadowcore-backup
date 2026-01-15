#!/bin/bash
echo "🖥️  SHADOWCORE DOMAIN MONITOR"
echo "============================="
date
echo ""
echo "🌐 Service Status:"
for svc in shadowcore-react-ui shadowcore-threat-api nginx; do
    status=$(systemctl is-active $svc 2>/dev/null || echo "not-found")
    if [ "$status" = "active" ]; then
        echo "✅ $svc: ACTIVE"
    else
        echo "❌ $svc: $status"
    fi
done
echo ""
echo "🧪 Domain Test:"
curl -s -H "Host: shadowcore.club" http://localhost/health | python3 -c "
import json
try:
    data = json.load(sys.stdin)
    print(✅ Health:, data.get(status, ?))
except:
    print(❌ Health failed)
"

