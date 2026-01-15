#!/usr/bin/env python3
"""
CLEAN ShadowCore Orchestrator - FIXED VERSION
"""
import json
import re
import asyncio
import time
from datetime import datetime
import redis
from neo4j import GraphDatabase
import os

print("🎯 SHADOWCORE CLEAN ORCHESTRATOR - FIXED")
print("=" * 60)
print("Proper threat detection with clean feeds")
print("=" * 60)

class CleanShadowCoreOrchestrator:
    def __init__(self):
        print("\n🔧 Initializing clean orchestrator...")
        
        # Connect to databases
        self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.neo4j_driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "Jonboy@123")
        )
        
        # Load clean threat cache
        self.threat_cache = self.load_clean_cache()
        
        print(f"  ✅ Redis: Connected")
        print(f"  ✅ Neo4j: Connected")
        print(f"  ✅ Threat Cache: {len(self.threat_cache)} CLEAN threats loaded")
        print("✅ Orchestrator ready with CLEAN intelligence")
    
    def load_clean_cache(self):
        """Load clean threat cache"""
        cache_file = "/opt/shadowcore/feeds/clean/threat_cache_clean.json"
        if os.path.exists(cache_file):
            try:
                with open(cache_file) as f:
                    cache = json.load(f)
                    print(f"  📦 Loaded from clean cache")
                    return cache
            except:
                pass
        
        # Fall back to processed cache
        cache_file = "/opt/shadowcore/feeds/processed/threat_cache.json"
        if os.path.exists(cache_file):
            try:
                with open(cache_file) as f:
                    cache = json.load(f)
                    print(f"  ⚠️  Loaded from processed cache (may contain noise)")
                    return cache
            except:
                pass
        
        return {}
    
    def is_valid_ip(self, ip):
        """Validate IP address"""
        ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        if not re.match(ip_pattern, ip):
            return False
        
        parts = ip.split('.')
        for part in parts:
            if not 0 <= int(part) <= 255:
                return False
        return True
    
    def check_threat_feeds(self, ioc):
        """Check if IOC exists in CLEAN threat feeds"""
        # Direct match
        if ioc in self.threat_cache:
            return self.threat_cache[ioc]
        
        # Special handling for IPs
        if self.is_valid_ip(ioc):
            return self.threat_cache.get(ioc)
        
        # For non-IP IOCs, check if they look malicious
        malicious_keywords = ['evil', 'malware', 'phish', 'hack', 'malicious', 'c2', 'botnet']
        if any(keyword in ioc.lower() for keyword in malicious_keywords):
            return {
                'type': 'suspicious',
                'source': 'heuristic',
                'threat_level': 'medium',
                'reason': 'Contains malicious keywords'
            }
        
        return None
    
    async def process_ioc(self, ioc):
        """Process IOC with CLEAN intelligence"""
        print(f"\n🔍 Processing: {ioc}")
        print("-" * 40)
        
        start_time = time.time()
        
        # Step 1: Check CLEAN threat cache
        print("1. 📡 Checking threat feeds...")
        threat_info = self.check_threat_feeds(ioc)
        
        if threat_info:
            print(f"   ✅ THREAT ANALYSIS")
            print(f"      Source: {threat_info.get('source', 'unknown')}")
            print(f"      Type: {threat_info.get('type', 'unknown')}")
            if 'malware' in threat_info:
                print(f"      Malware: {threat_info['malware']}")
            
            threat_level = threat_info.get('threat_level', 'high')
            confidence = 0.95 if threat_level == 'high' else 0.6
        else:
            print(f"   ℹ️  No match in threat feeds")
            
            # Heuristic analysis
            if self.is_valid_ip(ioc):
                # Check if it's a private/reserved IP
                if ioc.startswith(('10.', '192.168.', '172.16.', '127.', '169.254.')):
                    threat_level = 'low'
                    confidence = 0.1
                    print(f"   ℹ️  Private/reserved IP address")
                elif ioc in ['8.8.8.8', '1.1.1.1', '9.9.9.9']:
                    threat_level = 'low'
                    confidence = 0.1
                    print(f"   ℹ️  Known legitimate DNS server")
                else:
                    threat_level = 'low'
                    confidence = 0.3
            else:
                threat_level = 'low'
                confidence = 0.3
        
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
        
        # Step 4: Generate CLEAN report
        print("4. 📊 Generating intelligence report...")
        
        report = {
            'ioc': ioc,
            'timestamp': datetime.now().isoformat(),
            'processing_time': round(time.time() - start_time, 2),
            'threat_assessment': {
                'level': threat_level,
                'confidence': confidence,
                'summary': self.get_threat_summary(threat_info, ioc)
            },
            'intelligence_sources': {
                'osint_feeds': bool(threat_info and threat_info.get('source') != 'heuristic'),
                'heuristic_analysis': bool(threat_info and threat_info.get('source') == 'heuristic'),
                'knowledge_graph': bool(graph_info),
                'memory_cache': bool(cached)
            },
            'actions_recommended': self.get_recommended_actions(threat_level, threat_info),
            'correlation_score': 0.9 if threat_info else 0.4,
            'report_id': f"CLEAN-{int(time.time())}-{hash(ioc) % 10000:04d}",
            'threat_data': threat_info if threat_info else {}
        }
        
        # Step 5: Store in systems
        print("5. 💾 Storing in memory systems...")
        await self.store_results(ioc, report, threat_level)
        
        print(f"\n✅ Analysis complete in {report['processing_time']}s")
        print(f"📊 Threat Level: {threat_level.upper()}")
        print(f"🎯 Confidence: {confidence:.2f}")
        print(f"📋 Report ID: {report['report_id']}")
        
        return report
    
    def get_threat_summary(self, threat_info, ioc):
        """Get threat summary"""
        if not threat_info:
            if self.is_valid_ip(ioc):
                return f"Unknown public IP address"
            else:
                return f"Unknown IOC"
        
        source = threat_info.get('source', 'unknown')
        if source == 'heuristic':
            return threat_info.get('reason', 'Heuristic analysis')
        elif 'malware' in threat_info:
            return f"Known {threat_info['malware']} infrastructure"
        else:
            return f"Known threat from {source}"
    
    def get_recommended_actions(self, threat_level, threat_info):
        """Get recommended actions"""
        if threat_level == 'high':
            actions = ['Block immediately', 'Investigate endpoints', 'Alert SOC']
            if threat_info and 'malware' in threat_info:
                actions.append(f"Check for {threat_info['malware']} indicators")
            return actions
        elif threat_level == 'medium':
            return ['Monitor closely', 'Add to watchlist', 'Investigate']
        else:
            return ['Add to observables', 'Monitor periodically']
    
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
    
    def add_to_neo4j(self, ioc, report):
        """Add new threat to Neo4j - FIXED METHOD"""
        query = """
        MERGE (i:IOC {value: $ioc})
        SET i.type = $type,
            i.threat_level = $threat_level,
            i.source = $source,
            i.first_seen = timestamp(),
            i.last_updated = timestamp(),
            i.confidence = $confidence,
            i.malware = $malware
        RETURN i.value as added_ioc
        """
        
        try:
            with self.neo4j_driver.session() as session:
                threat_data = report.get('threat_data', {})
                malware = threat_data.get('malware', '')
                
                result = session.run(query,
                    ioc=ioc,
                    type=threat_data.get('type', 'unknown'),
                    threat_level=report['threat_assessment']['level'],
                    source=threat_data.get('source', 'unknown'),
                    confidence=report['threat_assessment']['confidence'],
                    malware=malware
                )
                record = result.single()
                if record:
                    print(f"   ✅ Added to knowledge graph: {record['added_ioc']}")
        except Exception as e:
            print(f"   ❌ Failed to add to Neo4j: {str(e)[:50]}")
    
    async def store_results(self, ioc, report, threat_level):
        """Store results in all memory systems"""
        # Store in Redis
        redis_key = f"analysis:{ioc}"
        self.redis.setex(redis_key, 3600, json.dumps(report))
        
        # Store in Neo4j if high threat and valid IP
        if threat_level == 'high' and self.is_valid_ip(ioc):
            if not await self.check_neo4j(ioc):
                self.add_to_neo4j(ioc, report)
        
        # Save to reports directory
        report_file = f"/opt/shadowcore/intelligence_reports/{report['report_id']}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

async def demo_clean_detection():
    """Demonstrate CLEAN threat detection"""
    print("\n🎯 DEMONSTRATING CLEAN THREAT DETECTION")
    print("=" * 50)
    
    orchestrator = CleanShadowCoreOrchestrator()
    
    # Test with mixed IOCs
    test_iocs = [
        # Real malicious IPs (from clean feeds)
        "162.243.103.246",  # Emotet C2 from Feodo Tracker
        "137.184.9.29",     # QakBot C2 from Feodo Tracker
        # Clean IPs
        "8.8.8.8",          # Google DNS
        "1.1.1.1",         # Cloudflare DNS
        # Suspicious domains
        "evil-traffic.com",
        "malware-distribution.net",
        # Legitimate domains
        "google.com",
        "github.com"
    ]
    
    print(f"🔍 Testing {len(test_iocs)} diverse IOCs")
    print("=" * 50)
    
    results = []
    threat_counts = {'high': 0, 'medium': 0, 'low': 0}
    
    for ioc in test_iocs:
        result = await orchestrator.process_ioc(ioc)
        results.append(result)
        
        threat_level = result['threat_assessment']['level']
        threat_counts[threat_level] += 1
        
        print()  # Empty line between analyses
    
    # Analysis summary
    print("=" * 50)
    print("📊 CLEAN ANALYSIS SUMMARY")
    print("=" * 50)
    print(f"📈 Total IOCs Analyzed: {len(results)}")
    print(f"🔴 HIGH Threats: {threat_counts['high']}")
    print(f"🟡 MEDIUM Threats: {threat_counts['medium']}")
    print(f"🟢 LOW Threats: {threat_counts['low']}")
    
    # Calculate accuracy (we know which are actually malicious)
    actual_malicious = ["162.243.103.246", "137.184.9.29"]
    detected_malicious = [r for r in results if r['ioc'] in actual_malicious and r['threat_assessment']['level'] == 'high']
    
    if actual_malicious:
        accuracy = (len(detected_malicious) / len(actual_malicious)) * 100
        print(f"🎯 Detection Accuracy: {accuracy:.1f}%")
    
    # Show detailed results
    print("\n📋 DETAILED RESULTS:")
    for result in results:
        ioc = result['ioc']
        level = result['threat_assessment']['level']
        conf = result['threat_assessment']['confidence']
        summary = result['threat_assessment']['summary']
        
        if level == 'high':
            print(f"  🔴 {ioc:25} -> HIGH     (confidence: {conf:.2f}) - {summary}")
        elif level == 'medium':
            print(f"  🟡 {ioc:25} -> MEDIUM   (confidence: {conf:.2f}) - {summary}")
        else:
            print(f"  🟢 {ioc:25} -> LOW      (confidence: {conf:.2f}) - {summary}")
    
    # Save comprehensive report
    batch_file = f"/opt/shadowcore/intelligence_reports/clean_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(batch_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_iocs': len(results),
                'threat_distribution': threat_counts,
                'detection_accuracy': f"{accuracy:.1f}%" if 'accuracy' in locals() else 'N/A'
            },
            'detailed_results': results
        }, f, indent=2)
    
    print(f"\n📁 Full report: {batch_file}")
    
    return results

async def quick_test():
    """Quick test function"""
    orchestrator = CleanShadowCoreOrchestrator()
    
    test_iocs = [
        "162.243.103.246",  # Should be HIGH (Emotet)
        "8.8.8.8",          # Should be LOW (Google DNS)
        "evil-traffic.com", # Should be MEDIUM (suspicious)
        "google.com"        # Should be LOW (legitimate)
    ]
    
    print("🔍 Quick Threat Detection Test:")
    print("-" * 40)
    
    for ioc in test_iocs:
        result = await orchestrator.process_ioc(ioc)
        level = result['threat_assessment']['level']
        conf = result['threat_assessment']['confidence']
        summary = result['threat_assessment']['summary']
        
        if level == 'high':
            print(f"  🔴 {ioc:25} -> HIGH     (confidence: {conf:.2f})")
        elif level == 'medium':
            print(f"  🟡 {ioc:25} -> MEDIUM   (confidence: {conf:.2f})")
        else:
            print(f"  🟢 {ioc:25} -> LOW      (confidence: {conf:.2f})")

if __name__ == "__main__":
    asyncio.run(demo_clean_detection())
