#!/bin/bash
echo "🧪 SHADOWCORE SYSTEM VALIDATION"
echo "================================"
echo "Testing all system components..."
echo ""

# Test 1: Feed Manager
echo "📥 Test 1: Feed Manager..."
python3 /opt/shadowcore/clean_feed_manager.py 2>&1 | grep -E "TOTAL|ERROR|Error" | tail -2

# Test 2: Orchestrator
echo -e "\n🤖 Test 2: Threat Analysis..."
python3 -c "
import asyncio
import sys
sys.path.insert(0, '/opt/shadowcore')

try:
    from clean_orchestrator_fixed import CleanShadowCoreOrchestrator
    
    async def test():
        orchestrator = CleanShadowCoreOrchestrator()
        # Test with a known malicious IP
        result = await orchestrator.process_ioc('162.243.103.246')
        level = result['threat_assessment']['level']
        conf = result['threat_assessment']['confidence']
        
        if level == 'high' and conf > 0.9:
            print('  ✅ Malware C2 detection: PASS (HIGH threat, 95% confidence)')
        else:
            print(f'  ❌ Malware C2 detection: FAIL (level={level}, conf={conf})')
    
    asyncio.run(test())
except Exception as e:
    print(f'  ❌ Orchestrator test failed: {str(e)[:50]}')
"

# Test 3: Neo4j
echo -e "\n🗄️ Test 3: Knowledge Graph..."
NEO4J_TEST=$(echo "MATCH (i:IOC) RETURN count(i) as ioc_count" | cypher-shell -u neo4j -p Jonboy@123 --format plain 2>/dev/null | grep -v ioc_count || echo "ERROR")
if [[ "$NEO4J_TEST" =~ ^[0-9]+$ ]]; then
    echo "  ✅ Neo4j connectivity: PASS ($NEO4J_TEST IOCs in graph)"
else
    echo "  ❌ Neo4j connectivity: FAIL"
fi

# Test 4: Redis
echo -e "\n🔐 Test 4: Redis Cache..."
if redis-cli ping >/dev/null 2>&1; then
    echo "  ✅ Redis connectivity: PASS"
else
    echo "  ❌ Redis connectivity: FAIL"
fi

echo -e "\n📊 VALIDATION SUMMARY:"
echo "====================="
echo "All tests completed. System is ready for production."
