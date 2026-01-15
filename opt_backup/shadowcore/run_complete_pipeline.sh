#!/bin/bash
echo "🚀 SHADOWCORE COMPLETE THREAT PIPELINE"
echo "========================================"
echo "Time: $(date)"
echo ""

# 1. Update threat feeds
echo "📥 1. Updating threat feeds..."
python3 /opt/shadowcore/feed_manager.py > /tmp/feed_output.txt 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Feeds updated successfully"
    FEED_THREATS=$(grep -o "TOTAL: [0-9]*" /tmp/feed_output.txt | grep -o "[0-9]*" || echo "0")
    echo "   Threats collected: $FEED_THREATS"
else
    echo "❌ Feed update failed"
fi

# 2. Run enhanced analysis
echo ""
echo "🤖 2. Running enhanced analysis..."
python3 /opt/shadowcore/enhanced_orchestrator.py > /tmp/orchestrator_output.txt 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Analysis completed"
    THREAT_COUNT=$(grep -o "Threats Found: [0-9]*" /tmp/orchestrator_output.txt | grep -o "[0-9]*" || echo "0")
    echo "   Threats analyzed: $THREAT_COUNT"
else
    echo "❌ Analysis failed"
fi

# 3. Update dashboard
echo ""
echo "📊 3. Updating dashboard..."
curl -s http://localhost:8020 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Dashboard is running"
    echo "   Access at: http://localhost:8020"
else
    echo "⚠️  Dashboard may not be running"
fi

# 4. Generate summary
echo ""
echo "📋 4. Pipeline Summary"
echo "========================================"
echo "Threat Feed Sources:"
ls /opt/shadowcore/feeds/processed/threats_*.json 2>/dev/null | wc -l | xargs echo "   - Files:"
echo "   - Latest: $(ls -t /opt/shadowcore/feeds/processed/threats_*.json 2>/dev/null | head -1 | xargs basename 2>/dev/null || echo 'None')"

echo ""
echo "Knowledge Graph Status:"
echo "MATCH (n) RETURN labels(n)[0] as type, count(n) as count ORDER BY type;" | cypher-shell -u neo4j -p Jonboy@123 --format plain 2>/dev/null || echo "   Neo4j not accessible"

echo ""
echo "Intelligence Reports:"
ls /opt/shadowcore/intelligence_reports/*.json 2>/dev/null | wc -l | xargs echo "   - Total reports:"
echo "   - Latest: $(ls -t /opt/shadowcore/intelligence_reports/*.json 2>/dev/null | head -1 | xargs basename 2>/dev/null || echo 'None')"

echo ""
echo "========================================"
echo "✅ Pipeline completed at $(date)"
echo "========================================"
