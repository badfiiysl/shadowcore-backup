#!/usr/bin/env python3
"""
Fixed ShadowCore Orchestrator - Properly checks threat feeds
"""
import json
import re
import asyncio
import time
from datetime import datetime
import redis
from neo4j import GraphDatabase
import os

print("🔧 SHADOWCORE FIXED ORCHESTRATOR")
print("=" * 60)
print("Now properly checking REAL threat feeds")
print("=" * 60)

class FixedShadowCoreOrchestrator:
    def __init__(self):
        print("\n🔧 Initializing fixed orchestrator...")
        
        # Connect to databases
        self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.neo4j_driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "Jonboy@123")
        )
        
        # Load threat cache from feeds
        self.threat_cache = self.load_threat_cache()
        
        print(f"  ✅ Redis: Connected")
        print(f"  ✅ Neo4j: Connected")
        print(f"  ✅ Threat Cache: {len(self.threat_cache)} known threats loaded")
        print("✅ Orchestrator ready with REAL feed intelligence")
    
    def load_threat_cache(self):
        """Load threat cache from feed processor"""
        cache_file = "/opt/shadowcore/feeds/processed/threat_cache.json"
        if os.path.exists(cache_file):
            try:
                with open(cache_file) as f:
                    return json.load(f)
            except Exception as e:
                print(f"  ❌ Error loading cache: {e}")
        return {}
    
    def check_threat_feeds(self, ioc):
        """Check if IOC exists in threat feeds (improved matching)"""
        # Direct match
        if ioc in self.threat_cache:
            return self.threat_cache[ioc]
        
        # IP address pattern matching
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        if re.match(ip_pattern, ioc):
            # Check if any similar IP in cache
            for threat_ip in self.threat_cache:
                if threat_ip == ioc or threat_ip.startswith(ioc.split('.')[0]):
                    return self.threat_cache[threat_ip]
        
        # Domain/URL matching
        if '://' in ioc or '.' in ioc:
            ioc_lower = ioc.lower()
            for threat in self.threat_cache.values():
                threat_ioc = threat.get('ioc', '').lower()
                if ioc_lower in threat_ioc or threat_ioc in ioc_lower:
                    return threat
        
        return None
    
    async def process_ioc(self, ioc):
        """Process IOC with IMPROVED feed intelligence"""
        print(f"\n🔍 Processing: {ioc}")
        print("-" * 40)
        
        start_time = time.time()
        
        # Step 1: Check threat cache (improved)
        print("1. 📡 Checking threat feeds...")
        threat_info = self.check_threat_feeds(ioc)
        
        if threat_info:
            print(f"   ✅ THREAT FOUND IN OSINT FEEDS")
            print(f"      Source: {threat_info.get('source', 'unknown')}")
            print(f"      Type: {threat_info.get('type', 'unknown')}")
            if threat_info.get('malware'):
                print(f"      Malware: {threat_info['malware']}")
            threat_level = 'high'
            confidence = 0.95
        else:
            print(f"   ℹ️  No match in threat feeds")
            # Default logic for unknown IOCs
            threat_level = 'low'
            confidence = 0.3
            
            # Heuristic: Check if looks malicious
            if any(x in ioc.lower() for x in ['evil', 'malicious', 'malware', 'phish', 'hack']):
                threat_level = 'medium'
                confidence = 0.6
        
        # Step 2: Check Neo4j knowledge graph
        print("2. 🗄️ Checking knowledge graph...")
        graph_info = await self.check_neo4j(ioc)
        if graph_info:
            print(f"   ✅ Found in knowledge graph")
            print(f"      Relations: {graph_info.get('relations', 0)}")
        
        # Step 3: Check Redis cache
        print("3. 🔍 Checking memory cache...")
        redis_key = f"analysis:{ioc}"
        cached = self.redis.get(redis_key)
        if cached:
            print(f"   ✅ Cached analysis found")
        
        # Step 4: Generate enhanced report
        print("4. 📊 Generating intelligence report...")
        
        report = {
            'ioc': ioc,
            'timestamp': datetime.now().isoformat(),
            'processing_time': round(time.time() - start_time, 2),
            'threat_assessment': {
                'level': threat_level,
                'confidence': confidence,
                'summary': 'Matched in OSINT feeds' if threat_info else 'No feed matches'
            },
            'intelligence_sources': {
                'osint_feeds': bool(threat_info),
                'knowledge_graph': bool(graph_info),
                'memory_cache': bool(cached)
            },
            'actions_recommended': self.get_recommended_actions(threat_level),
            'correlation_score': 0.9 if threat_info else 0.4,
            'report_id': f"FIXED-{int(time.time())}-{hash(ioc) % 10000:04d}",
            'feed_data': threat_info if threat_info else {}
        }
        
        # Step 5: Store in systems
        print("5. 💾 Storing in memory systems...")
        await self.store_results(ioc, report)
        
        print(f"\n✅ Analysis complete in {report['processing_time']}s")
        print(f"📊 Threat Level: {threat_level.upper()}")
        print(f"🎯 Confidence: {confidence}")
        print(f"📋 Report ID: {report['report_id']}")
        
        return report
    
    async def check_neo4j(self, ioc):
        """Check Neo4j knowledge graph"""
        query = """
        MATCH (i:IOC {value: $ioc})
        OPTIONAL MATCH (i)-[r]-(related)
        RETURN i.value as ioc, 
               COUNT(r) as relations,
               COLLECT(DISTINCT labels(related)) as related_labels
        """
        
        try:
            with self.neo4j_driver.session() as session:
                result = session.run(query, ioc=ioc)
                record = result.single()
                
                if record and record['ioc']:
                    return {
                        'relations': record['relations'],
                        'related_entities': record['related_labels']
                    }
        except Exception as e:
            print(f"   ❌ Neo4j error: {str(e)[:50]}")
        
        return None
    
    def get_recommended_actions(self, threat_level):
        """Get recommended actions based on threat level"""
        if threat_level == 'high':
            return ['BLOCK immediately', 'Investigate endpoints', 'Alert SOC', 'Update firewall']
        elif threat_level == 'medium':
            return ['Monitor closely', 'Add to watchlist', 'Investigate', 'Log activity']
        else:
            return ['Add to observables', 'Monitor', 'Check periodically']
    
    async def store_results(self, ioc, report):
        """Store results in all memory systems"""
        # Store in Redis
        redis_key = f"analysis:{ioc}"
        self.redis.setex(redis_key, 3600, json.dumps(report))
        
        # Store in Neo4j if high threat
        if report['threat_assessment']['level'] == 'high' and not await self.check_neo4j(ioc):
            self.add_to_neo4j(ioc, report)
        
        # Save to reports directory
        report_file = f"/opt/shadowcore/intelligence_reports/{report['report_id']}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
    
    def add_to_neo4j(self, ioc, report):
        """Add new threat to Neo4j"""
        query = """
        MERGE (i:IOC {value: $ioc})
        SET i.type = $type,
            i.threat_level = $threat_level,
            i.source = $source,
            i.first_seen = timestamp(),
            i.last_updated = timestamp(),
            i.confidence = $confidence
        RETURN i.value as added_ioc
        """
        
        try:
            with self.neo4j_driver.session() as session:
                feed_data = report.get('feed_data', {})
                result = session.run(query,
                    ioc=ioc,
                    type=feed_data.get('type', 'unknown'),
                    threat_level=report['threat_assessment']['level'],
                    source=feed_data.get('source', 'threat_feed'),
                    confidence=report['threat_assessment']['confidence']
                )
                print(f"   ✅ Added HIGH threat to knowledge graph")
        except Exception as e:
            print(f"   ❌ Failed to add to Neo4j: {str(e)[:50]}")

async def demo_with_real_threats():
    """Demonstrate with REAL threats from feeds"""
    print("\n🎯 DEMONSTRATING WITH REAL THREATS FROM FEEDS")
    print("=" * 50)
    
    # Load actual malicious IPs from cache
    with open('/opt/shadowcore/feeds/processed/threat_cache.json') as f:
        threat_cache = json.load(f)
    
    # Get some actual malicious IPs
    malicious_ips = list(threat_cache.keys())[:10]
    
    print(f"📊 Loaded {len(malicious_ips)} real malicious IPs from feeds")
    print(f"📋 Sample: {malicious_ips[:3]}")
    
    orchestrator = FixedShadowCoreOrchestrator()
    
    # Test with REAL malicious IPs
    test_iocs = [
        malicious_ips[0],  # First malicious IP from feeds
        malicious_ips[3],  # Another malicious IP
        "8.8.8.8",        # Google DNS (clean)
        "evil-traffic.com", # Suspicious domain
        "https://legit-site.com" # Clean URL
    ]
    
    print(f"\n🔍 Testing {len(test_iocs)} IOCs (including REAL threats)")
    print("=" * 50)
    
    results = []
    for ioc in test_iocs:
        result = await orchestrator.process_ioc(ioc)
        results.append(result)
        print()  # Empty line between analyses
    
    # Analyze results
    high_threats = [r for r in results if r['threat_assessment']['level'] == 'high']
    medium_threats = [r for r in results if r['threat_assessment']['level'] == 'medium']
    
    print("=" * 50)
    print("📦 REAL THREAT ANALYSIS COMPLETE")
    print("=" * 50)
    print(f"📊 Total IOCs: {len(results)}")
    print(f"🔴 HIGH Threats: {len(high_threats)}")
    print(f"🟡 MEDIUM Threats: {len(medium_threats)}")
    print(f"🟢 LOW Threats: {len(results) - len(high_threats) - len(medium_threats)}")
    
    # Save batch report
    batch_file = f"/opt/shadowcore/intelligence_reports/real_threats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(batch_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_iocs': len(results),
                'high_threats': len(high_threats),
                'medium_threats': len(medium_threats),
                'low_threats': len(results) - len(high_threats) - len(medium_threats)
            },
            'reports': results
        }, f, indent=2)
    
    print(f"📁 Detailed report: {batch_file}")
    
    # Show threat detection rate
    if len(malicious_ips) > 0:
        detection_rate = (len(high_threats) / 2) * 100  # We tested 2 malicious IPs
        print(f"🎯 Threat Detection Rate: {detection_rate:.1f}%")
    
    return results

if __name__ == "__main__":
    asyncio.run(demo_with_real_threats())
