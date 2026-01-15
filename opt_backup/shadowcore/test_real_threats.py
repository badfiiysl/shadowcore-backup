#!/usr/bin/env python3
"""
Test ShadowCore with REAL malicious IOCs from feeds
"""
import json
import random

print("🎯 TESTING WITH REAL MALICIOUS THREATS")
print("=" * 60)

# Load threat cache
with open('/opt/shadowcore/feeds/processed/threat_cache.json') as f:
    threat_cache = json.load(f)

print(f"📊 Threat cache loaded: {len(threat_cache)} known threats")

# Get some actual malicious IPs
malicious_ips = list(threat_cache.keys())[:20]  # First 20 threats
print(f"\n🔍 Sample malicious IPs from feeds:")
for i, ip in enumerate(malicious_ips[:5]):
    threat = threat_cache[ip]
    print(f"  {i+1}. {ip} - {threat.get('type', 'unknown')} ({threat.get('source', 'unknown')})")

# Create test cases with KNOWN malicious IPs
test_cases = {
    "KNOWN_MALICIOUS": random.sample(malicious_ips, 5),
    "CLEAN_IPS": ["8.8.8.8", "1.1.1.1", "9.9.9.9"],
    "SUSPICIOUS_DOMAINS": ["evil-traffic.com", "malware-distribution.net", "phishing-site.org"]
}

print(f"\n🚀 Test cases prepared:")
for category, iocs in test_cases.items():
    print(f"  {category}: {len(iocs)} IOCs")

# Save test cases
with open('/opt/shadowcore/test_cases_real.json', 'w') as f:
    json.dump(test_cases, f, indent=2)

print(f"\n💾 Test cases saved to: /opt/shadowcore/test_cases_real.json")

print("\n📋 QUICK TEST COMMANDS:")
print("1. Test a known malicious IP:")
print('   python3 -c "')
print('   import json')
print('   with open(\'/opt/shadowcore/feeds/processed/threat_cache.json\') as f:')
print('       threats = json.load(f)')
print('   ips = list(threats.keys())')
print('   print(f\"First malicious IP: {ips[0]}\")')
print('   "')

print("\n2. Test with enhanced orchestrator:")
print('   python3 /opt/shadowcore/enhanced_orchestrator.py')
print('\n   OR create custom test:')
print('   cat > test_specific.py << \"TESTEOF\"')
print('   import asyncio')
print('   import sys')
print('   sys.path.insert(0, \'/opt/shadowcore\')')
print('   from enhanced_orchestrator import EnhancedShadowCoreOrchestrator')
print('   ')
print('   async def test():')
print('       orchestrator = EnhancedShadowCoreOrchestrator()')
print('       # Test with KNOWN malicious IP')
print('       result = await orchestrator.process_ioc(\"185.222.202.168\")')
print('       print(f\"Threat level: {result[\"threat_assessment\"][\"level\"]}\")')
print('       print(f\"Confidence: {result[\"threat_assessment\"][\"confidence\"]}\")')
print('   ')
print('   asyncio.run(test())')
print('   TESTEOF')
