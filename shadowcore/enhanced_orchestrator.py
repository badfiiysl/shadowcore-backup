#!/usr/bin/env python3
"""
ShadowCore Enhanced Orchestrator with REAL OSINT feed integration
"""
import asyncio
import json
import time
from datetime import datetime
import redis
from neo4j import GraphDatabase
import os

print("🤖 SHADOWCORE ENHANCED ORCHESTRATOR")
print("=" * 60)
print("Now with REAL threat feed integration")
print("=" * 60)

class EnhancedShadowCoreOrchestrator:
    def __init__(self):
        print("\n🔧 Initializing enhanced orchestrator...")
        
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
        print("✅ Orchestrator ready with feed intelligence")
    
    def load_threat_cache(self):
        """Load threat cache from feed processor"""
        cache_file = "/opt/shadowcore/feeds/processed/threat_cache.json"
        if os.path.exists(cache_file):
            try:
                with open(cache_file) as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    async def process_ioc(self, ioc):
        """Process IOC with REAL feed intelligence"""
        print(f"\n🔍 Processing: {ioc}")
        print("-" * 40)
        
        start_time = time.time()
        
        # Step 1: Check threat cache (instant)
        print("1. 📡 Checking threat feeds...")
        if ioc in self.threat_cache:
            threat_info = self.threat_cache[ioc]
            print(f"   ✅ THREAT FOUND IN OSINT FEEDS")
            print(f"      Source: {threat_info.get('source', 'unknown')}")
            print(f"      Type: {threat_info.get('type', 'unknown')}")
            threat_level = threat_info.get('threat_level', 'medium')
            confidence = 0.9
        else:
            print(f"   ℹ️  No match in threat feeds")
            threat_level = 'low'
            confidence = 0.3
        
        # Step 2: Check Neo4j knowledge graph
        print("2. 🗄️ Checking knowledge graph...")
        graph_info = await self.check_neo4j(ioc)
        if graph_info:
            print(f"   ✅ Found in knowledge graph")
            print(f"      Relations: {graph_info.get('relations', 0)}")
            if graph_info.get('malware'):
                print(f"      Malware: {graph_info['malware']}")
        
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
                'summary': 'Matched in OSINT feeds' if ioc in self.threat_cache else 'No feed matches'
            },
            'intelligence_sources': {
                'osint_feeds': ioc in self.threat_cache,
                'knowledge_graph': bool(graph_info),
                'memory_cache': bool(cached)
            },
            'actions_recommended': self.get_recommended_actions(threat_level),
            'correlation_score': 0.8 if ioc in self.threat_cache else 0.4,
            'report_id': f"ENHANCED-{int(time.time())}-{hash(ioc) % 10000:04d}",
            'feed_data': self.threat_cache.get(ioc, {})
        }
        
        # Step 5: Store in systems
        print("5. 💾 Storing in memory systems...")
        await self.store_results(ioc, report)
        
        print(f"\n✅ Analysis complete in {report['processing_time']}s")
        print(f"📊 Threat Level: {threat_level.upper()}")
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
            return ['Block immediately', 'Investigate endpoints', 'Alert SOC', 'Update firewall rules']
        elif threat_level == 'medium':
            return ['Monitor traffic', 'Add to watchlist', 'Investigate', 'Log all activity']
        else:
            return ['Add to observables', 'Monitor for changes', 'Check periodically']
    
    async def store_results(self, ioc, report):
        """Store results in all memory systems"""
        # Store in Redis
        redis_key = f"analysis:{ioc}"
        self.redis.setex(redis_key, 3600, json.dumps(report))
        
        # Store in Neo4j if new threat
        if ioc in self.threat_cache and not await self.check_neo4j(ioc):
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
            i.last_updated = timestamp()
        RETURN i.value as added_ioc
        """
        
        try:
            with self.neo4j_driver.session() as session:
                feed_data = report.get('feed_data', {})
                result = session.run(query, 
                    ioc=ioc,
                    type=feed_data.get('type', 'unknown'),
                    threat_level=report['threat_assessment']['level'],
                    source=feed_data.get('source', 'unknown')
                )
                print(f"   ✅ Added to knowledge graph")
        except Exception as e:
            print(f"   ❌ Failed to add to Neo4j: {str(e)[:50]}")

async def demo():
    """Demonstrate the enhanced orchestrator"""
    print("\n🎯 DEMONSTRATING WITH REAL THREATS")
    print("=" * 50)
    
    orchestrator = EnhancedShadowCoreOrchestrator()
    
    # Test with some example IOCs
    test_iocs = [
        "185.220.100.255",  # Known Tor exit node
        "evil-traffic.com",
        "https://malicious.site/payload",
        "8.8.8.8",  # Google DNS (should be clean)
        "159.65.219.189"    # DigitalOcean IP
    ]
    
    results = []
    for ioc in test_iocs:
        result = await orchestrator.process_ioc(ioc)
        results.append(result)
        print()  # Empty line between analyses
    
    # Save batch report
    batch_file = f"/opt/shadowcore/intelligence_reports/batch_enhanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(batch_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_iocs': len(results),
            'threats_found': len([r for r in results if r['threat_assessment']['level'] != 'low']),
            'reports': results
        }, f, indent=2)
    
    print("=" * 50)
    print("📦 BATCH ANALYSIS COMPLETE")
    print("=" * 50)
    print(f"📊 Total IOCs: {len(results)}")
    print(f"🔴 Threats Found: {len([r for r in results if r['threat_assessment']['level'] != 'low'])}")
    print(f"📁 Batch Report: {batch_file}")
    print("\n🚀 Next: Run the feed manager first to get real threat data!")
    print("   python3 /opt/shadowcore/feed_manager.py")

if __name__ == "__main__":
    asyncio.run(demo())
