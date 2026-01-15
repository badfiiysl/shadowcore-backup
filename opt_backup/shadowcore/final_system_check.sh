#!/bin/bash
echo "🔍 SHADOWCORE FINAL SYSTEM CHECK"
echo "========================================"
echo ""
echo "📅 $(date)"
echo ""

echo "🏗️  ARCHITECTURE STATUS:"
echo "---------------------"

# Check all services
declare -A services=(
    ["Agent Manager - REST API"]="8000"
    ["Agent Manager - Threat API"]="8003"
    ["Agent Manager - Main API"]="8004"
    ["Agent Manager - Auth API"]="8006"
    ["Worker Pool - WebSocket"]="8083"
    ["Worker Pool - Proxy"]="8080"
    ["Worker Pool - Node Worker"]="8002"
    ["Worker Pool - Node API"]="8081"
    ["AI Engine - shadowbrain"]="8001"
    ["AI Engine - Ollama"]="11434"
    ["AI Engine - Qdrant"]="6333"
    ["OSINT Engine - Threat Insight"]="9090"
    ["OSINT Engine - Data Server"]="8005"
    ["Memory - Neo4j Bolt"]="7687"
    ["Memory - Neo4j HTTP"]="7474"
    ["Memory - Redis"]="6379"
    ["Memory - PostgreSQL"]="5432"
    ["Dashboard"]="8020"
    ["Monitoring - Grafana"]="3000"
)

healthy=0
total=${#services[@]}

for name in "${!services[@]}"; do
    port=${services[$name]}
    
    if timeout 1 bash -c "cat < /dev/null > /dev/tcp/localhost/$port" 2>/dev/null; then
        echo "✅ $name (:$port)"
        ((healthy++))
    else
        echo "❌ $name (:$port)"
    fi
done

echo ""
echo "📊 HEALTH SCORE: $healthy/$total ($((healthy*100/total))%)"

echo ""
echo "📁 DATA STATUS:"
echo "---------------------"

# Check data files
data_files=(
    "/opt/shadowcore/threat_intelligence_graph.json"
    "/opt/shadowcore/threat_intelligence_graph_fixed.json" 
    "/opt/shadowcore/simple_threat_graph.json"
    "/opt/shadowcore/threat_embeddings.json"
    "/opt/shadowcore/dashboard_data.json"
    "/opt/shadowcore/system_summary.json"
    "/opt/shadowcore/intelligence_reports/"
)

for file in "${data_files[@]}"; do
    if [ -e "$file" ]; then
        if [ -d "$file" ]; then
            count=$(ls -1 "$file" 2>/dev/null | wc -l)
            echo "✅ $(basename "$file") - $count files"
        else
            size=$(stat -c%s "$file" 2>/dev/null || echo "0")
            human_size=$(numfmt --to=iec $size 2>/dev/null || echo "${size}B")
            echo "✅ $(basename "$file") - $human_size"
        fi
    else
        echo "⚠️  $(basename "$file") - Not found"
    fi
done

echo ""
echo "🧠 NEO4J STATUS:"
echo "---------------------"

# Check Neo4j data
if command -v cypher-shell &> /dev/null; then
    echo "Checking Neo4j data..."
    
    # Count nodes
    node_count=$(cypher-shell -u neo4j -p Jonboy@123 --format plain "MATCH (n) RETURN count(n)" 2>/dev/null | tail -1)
    echo "✅ Total nodes: ${node_count:-0}"
    
    # Count by type
    echo "Node types:"
    cypher-shell -u neo4j -p Jonboy@123 --format plain "MATCH (n) RETURN labels(n)[0] as type, count(n) as count ORDER BY count DESC" 2>/dev/null | tail -5
    
else
    echo "⚠️  cypher-shell not available"
fi

echo ""
echo "🚀 QUICK START:"
echo "---------------------"
echo "1. Run analysis:   python3 /opt/shadowcore/final_orchestrator.py"
echo "2. Run test:       python3 /opt/shadowcore/final_orchestrator.py test"
echo "3. View dashboard: http://localhost:8020"
echo "4. Neo4j browser:  http://localhost:7474 (neo4j/Jonboy@123)"
echo "5. View reports:   ls -la /opt/shadowcore/intelligence_reports/"

echo ""
echo "🎯 SYSTEM CAPABILITIES:"
echo "---------------------"
echo "• ✅ Agent Manager - Task scheduling & ACL"
echo "• ✅ Worker Pool - IOC processing & crawling"
echo "• ✅ AI Engines - Cognitive analysis & embeddings"
echo "• ✅ OSINT Engine - Threat feed ingestion"
echo "• ✅ Memory Systems - Graph + vector + cache storage"
echo "• ✅ Orchestrator - Autonomous coordination"

echo ""
echo "========================================"
if [ $healthy -eq $total ]; then
    echo "🎉 SYSTEM IS FULLY OPERATIONAL!"
else
    echo "⚠️  SYSTEM HAS $(($total - $healthy)) ISSUES"
fi
echo "========================================"
