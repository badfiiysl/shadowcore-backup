#!/bin/bash
echo "🔍 SHADOWCORE SYSTEM MONITOR"
echo "============================="
echo "Time: $(date)"
echo ""

# System Status
echo "📊 SYSTEM STATUS:"
echo "----------------"
echo -n "Neo4j: "
if systemctl is-active neo4j >/dev/null 2>&1; then
    echo -e "\033[0;32mACTIVE\033[0m"
else
    echo -e "\033[0;31mINACTIVE\033[0m"
fi

echo -n "Redis: "
if systemctl is-active redis-server >/dev/null 2>&1; then
    echo -e "\033[0;32mACTIVE\033[0m"
else
    echo -e "\033[0;31mINACTIVE\033[0m"
fi

echo -n "Dashboard: "
if curl -s http://localhost:8020 >/dev/null 2>&1; then
    echo -e "\033[0;32mACTIVE\033[0m"
else
    echo -e "\033[0;31mINACTIVE\033[0m"
fi

# Threat Intelligence
echo -e "\n🎯 THREAT INTELLIGENCE:"
echo "----------------------"
THREAT_CACHE="/opt/shadowcore/feeds/processed/threat_cache.json"
if [ -f "$THREAT_CACHE" ]; then
    THREAT_COUNT=$(python3 -c "import json; print(len(json.load(open('$THREAT_CACHE'))))")
    echo "Known threats: $THREAT_COUNT"
else
    echo "Known threats: 0"
fi

REPORT_COUNT=$(ls /opt/shadowcore/intelligence_reports/*.json 2>/dev/null | wc -l)
echo "Analysis reports: $REPORT_COUNT"

# Recent Threats
echo -e "\n🔍 RECENT THREAT DETECTIONS:"
echo "----------------------------"
if [ -f "$THREAT_CACHE" ] && [ $(python3 -c "import json; print(len(json.load(open('$THREAT_CACHE'))))") -gt 0 ]; then
    python3 -c "
import json, random
with open('$THREAT_CACHE') as f:
    threats = json.load(f)

if threats:
    print('Sample of known malicious IPs:')
    sample = random.sample(list(threats.keys()), min(5, len(threats)))
    for i, ip in enumerate(sample):
        data = threats[ip]
        malware = data.get('malware', 'Unknown')
        source = data.get('source', 'unknown')
        print(f'  {i+1}. {ip} - {malware} ({source})')
else:
    print('  No threats in cache')
"
else
    echo "  No threat data available"
fi

echo -e "\n🚀 QUICK ACTIONS:"
echo "----------------"
echo "1. View Dashboard: http://localhost:8020"
echo "2. Analyze IOC:    python3 /opt/shadowcore/clean_orchestrator_fixed.py"
echo "3. Update Feeds:   python3 /opt/shadowcore/clean_feed_manager.py"
echo "4. View Reports:   ls -la /opt/shadowcore/intelligence_reports/"
echo ""
echo "✅ System monitoring complete"
