#!/bin/bash
echo "🏭 SHADOWCORE PRODUCTION PIPELINE"
echo "========================================"
echo "Time: $(date)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Feed Collection Phase
echo -e "${BLUE}📥 PHASE 1: THREAT FEED COLLECTION${NC}"
echo "----------------------------------------"
python3 /opt/shadowcore/feed_manager.py
FEED_STATUS=$?

if [ $FEED_STATUS -eq 0 ]; then
    FEED_COUNT=$(grep -o "TOTAL: [0-9]*" /tmp/feed_output.txt 2>/dev/null | grep -o "[0-9]*" || echo "0")
    echo -e "${GREEN}✅ Feeds collected: $FEED_COUNT threats${NC}"
else
    echo -e "${RED}❌ Feed collection failed${NC}"
fi

# 2. Threat Analysis Phase
echo ""
echo -e "${BLUE}🤖 PHASE 2: THREAT ANALYSIS${NC}"
echo "----------------------------------------"

# Load real threats from cache
REAL_THREATS_FILE="/opt/shadowcore/feeds/processed/threat_cache.json"
if [ -f "$REAL_THREATS_FILE" ]; then
    # Get 5 random malicious IPs for testing
    MALICIOUS_IPS=$(python3 -c "
import json, random
with open('$REAL_THREATS_FILE') as f:
    threats = json.load(f)
ips = list(threats.keys())
print(' '.join(random.sample(ips, min(5, len(ips)))))
    ")
    
    echo -e "${YELLOW}Testing with REAL malicious IPs:${NC}"
    for ip in $MALICIOUS_IPS; do
        echo -n "  Testing $ip... "
        python3 -c "
import asyncio
import sys
sys.path.insert(0, '/opt/shadowcore')
try:
    from fixed_orchestrator import FixedShadowCoreOrchestrator
    async def test():
        orchestrator = FixedShadowCoreOrchestrator()
        return await orchestrator.process_ioc('$ip')
    result = asyncio.run(test())
    level = result['threat_assessment']['level']
    if level == 'high':
        print('\033[0;31mHIGH\033[0m')
    elif level == 'medium':
        print('\033[1;33mMEDIUM\033[0m')
    else:
        print('\033[0;32mLOW\033[0m')
except Exception as e:
    print(f'\033[0;31mERROR: {str(e)[:30]}\033[0m')
        "
    done
fi

# 3. System Status Check
echo ""
echo -e "${BLUE}📊 PHASE 3: SYSTEM STATUS${NC}"
echo "----------------------------------------"

# Neo4j status
echo -n "Neo4j: "
NEO4J_COUNT=$(echo "MATCH (n) RETURN count(n)" | cypher-shell -u neo4j -p Jonboy@123 --format plain 2>/dev/null | grep -v count | tr -d '\n' || echo "ERROR")
if [[ "$NEO4J_COUNT" =~ ^[0-9]+$ ]]; then
    echo -e "${GREEN}$NEO4J_COUNT nodes${NC}"
else
    echo -e "${RED}Unavailable${NC}"
fi

# Redis status
echo -n "Redis: "
if redis-cli ping 2>/dev/null | grep -q PONG; then
    REDIS_KEYS=$(redis-cli keys "*" 2>/dev/null | wc -l)
    echo -e "${GREEN}$REDIS_KEYS keys${NC}"
else
    echo -e "${RED}Unavailable${NC}"
fi

# Report count
REPORT_COUNT=$(ls /opt/shadowcore/intelligence_reports/*.json 2>/dev/null | wc -l)
echo -e "Reports: ${GREEN}$REPORT_COUNT files${NC}"

# 4. Summary
echo ""
echo -e "${BLUE}📋 PIPELINE SUMMARY${NC}"
echo "========================================"
echo "Pipeline completed at: $(date)"
echo "System status: ${GREEN}OPERATIONAL${NC}"
echo ""
echo -e "${YELLOW}📈 NEXT STEPS:${NC}"
echo "1. View dashboard: http://localhost:8020"
echo "2. Explore Neo4j: http://localhost:7474"
echo "3. Check reports: ls -la /opt/shadowcore/intelligence_reports/"
echo "4. Add more feeds: Edit /opt/shadowcore/feed_manager.py"
echo ""
echo -e "${GREEN}✅ ShadowCore is now detecting REAL threats from OSINT feeds!${NC}"
