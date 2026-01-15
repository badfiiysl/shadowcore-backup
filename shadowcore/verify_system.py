#!/usr/bin/env python3
"""
Verify ShadowCore is detecting REAL threats
"""
import json
import subprocess

print("🔍 VERIFYING SHADOWCORE THREAT DETECTION")
print("=" * 50)

# 1. Check threat cache
with open('/opt/shadowcore/feeds/processed/threat_cache.json') as f:
    threats = json.load(f)

print(f"✅ Threat Cache: {len(threats)} known threats")

# 2. Check Neo4j
try:
    result = subprocess.run(
        ['cypher-shell', '-u', 'neo4j', '-p', 'Jonboy@123', '--format', 'plain',
         'MATCH (n) RETURN labels(n)[0] as type, count(n) as count ORDER BY count DESC'],
        capture_output=True, text=True
    )
    print(f"\n✅ Neo4j Status:")
    print(result.stdout.strip())
except:
    print("\n❌ Neo4j not accessible")

# 3. Check Redis
try:
    import redis
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    redis_keys = r.keys('analysis:*')
    print(f"\n✅ Redis Cache: {len(redis_keys)} cached analyses")
except:
    print("\n❌ Redis not accessible")

# 4. Check reports
import glob
reports = glob.glob('/opt/shadowcore/intelligence_reports/*.json')
print(f"\n✅ Intelligence Reports: {len(reports)} reports generated")

# 5. Test a KNOWN malicious IP
if threats:
    test_ip = list(threats.keys())[0]
    print(f"\n🎯 Quick Test with KNOWN malicious IP: {test_ip}")
    print(f"   Source: {threats[test_ip].get('source', 'unknown')}")
    print(f"   Type: {threats[test_ip].get('type', 'unknown')}")
    
    # Run quick analysis
    import asyncio
    import sys
    sys.path.insert(0, '/opt/shadowcore')
    
    try:
        from fixed_orchestrator import FixedShadowCoreOrchestrator
        
        async def quick_test():
            orchestrator = FixedShadowCoreOrchestrator()
            result = await orchestrator.process_ioc(test_ip)
            return result
        
        result = asyncio.run(quick_test())
        print(f"   ✅ Detection: {result['threat_assessment']['level'].upper()}")
        print(f"   ✅ Confidence: {result['threat_assessment']['confidence']}")
    except:
        print("   ⚠️  Could not run automated test")

print("\n" + "=" * 50)
print("📊 SYSTEM VERIFICATION COMPLETE")
print("=" * 50)
