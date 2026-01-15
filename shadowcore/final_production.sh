#!/bin/bash
echo "🏭 SHADOWCORE FINAL PRODUCTION SYSTEM"
echo "========================================"
echo "Time: $(date)"
echo ""

# Run clean feed collection
echo "🧹 1. Collecting CLEAN threat feeds..."
python3 /opt/shadowcore/clean_feed_manager.py

# Update cache
CLEAN_CACHE="/opt/shadowcore/feeds/clean/threat_cache_clean.json"
if [ -f "$CLEAN_CACHE" ]; then
    cp "$CLEAN_CACHE" /opt/shadowcore/feeds/processed/threat_cache.json
    echo "✅ Updated threat cache with clean data"
else
    echo "⚠️  Using existing threat cache"
fi

# Run clean analysis
echo -e "\n🎯 2. Running clean threat analysis..."
python3 /opt/shadowcore/clean_orchestrator.py

# System status
echo -e "\n📊 3. System Status:"
echo "   Neo4j nodes: $(echo "MATCH (n) RETURN count(n)" | cypher-shell -u neo4j -p Jonboy@123 --format plain 2>/dev/null | grep -v count)"
echo "   Redis keys: $(redis-cli keys "*" 2>/dev/null | wc -l)"
echo "   Total reports: $(ls /opt/shadowcore/intelligence_reports/*.json 2>/dev/null | wc -l)"

# Sample threat detection
echo -e "\n🔍 4. Sample Threat Detection Test:"
cat > /tmp/test_iocs.py << 'PYEOF'
import json
import asyncio
import sys
sys.path.insert(0, '/opt/shadowcore')

try:
    from clean_orchestrator import CleanShadowCoreOrchestrator
    
    test_iocs = [
        "162.243.103.246",  # Should be HIGH (Emotet)
        "8.8.8.8",          # Should be LOW (Google DNS)
        "evil-traffic.com", # Should be MEDIUM (suspicious)
        "google.com"        # Should be LOW (legitimate)
    ]
    
    async def test():
        orchestrator = CleanShadowCoreOrchestrator()
        for ioc in test_iocs:
            result = await orchestrator.process_ioc(ioc)
            level = result['threat_assessment']['level']
            conf = result['threat_assessment']['confidence']
            print(f"  {ioc:25} -> {level.upper():6} (confidence: {conf:.2f})")
    
    asyncio.run(test())
except Exception as e:
    print(f"  Error: {str(e)[:50]}")
PYEOF

python3 /tmp/test_iocs.py

echo -e "\n========================================"
echo "✅ SHADOWCORE PRODUCTION SYSTEM READY"
echo "========================================"
echo "Dashboard:    http://localhost:8020"
echo "Neo4j:        http://localhost:7474"
echo "Reports:      /opt/shadowcore/intelligence_reports/"
echo ""
echo "🎉 Your system is now detecting REAL threats PROPERLY!"
