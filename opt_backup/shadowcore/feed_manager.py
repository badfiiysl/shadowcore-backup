#!/usr/bin/env python3
"""
ShadowCore Simple Feed Manager - Gets you REAL threat data
"""
import json
import csv
import asyncio
import aiohttp
from datetime import datetime
import os
import sys

print("🚀 SHADOWCORE FEED MANAGER")
print("=" * 50)

class SimpleFeedManager:
    def __init__(self):
        self.feeds = {
            # Working feeds that don't require API keys
            'sslbl': 'https://sslbl.abuse.ch/blacklist/sslblacklist.csv',
            'feodo': 'https://feodotracker.abuse.ch/downloads/ipblocklist.csv',
            'blocklist_de': 'https://lists.blocklist.de/lists/all.txt',
            'urlhaus': 'https://urlhaus.abuse.ch/downloads/csv_recent/',
            'phishtank': 'http://data.phishtank.com/data/online-valid.json'
        }
        
        # Create output directory
        os.makedirs('/opt/shadowcore/feeds/processed', exist_ok=True)
    
    async def fetch_feed(self, name, url):
        """Fetch a single threat feed"""
        try:
            headers = {
                'User-Agent': 'ShadowCore Threat Intelligence/1.0'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        content = await response.text()
                        return await self.parse_feed(name, content, url)
                    else:
                        print(f"  ❌ {name}: HTTP {response.status}")
                        return []
        except Exception as e:
            print(f"  ❌ {name}: Error - {str(e)[:50]}...")
            return []
    
    async def parse_feed(self, name, content, url):
        """Parse different feed formats"""
        threats = []
        
        if 'sslbl' in name or 'feodo' in name or 'urlhaus' in name:
            # CSV format
            lines = content.strip().split('\n')
            for line in lines:
                if line.startswith('#') or not line.strip():
                    continue
                
                parts = line.split(',')
                if parts:
                    if 'sslbl' in name:
                        # SSL Blacklist format: Listingdate,Destination IP,Destination Port,Source,Malware
                        if len(parts) >= 5:
                            threats.append({
                                'ioc': parts[1].strip(),
                                'type': 'ip',
                                'port': parts[2].strip(),
                                'malware': parts[4].strip(),
                                'source': 'sslbl',
                                'first_seen': parts[0].strip()
                            })
                    elif 'feodo' in name:
                        # Feodo Tracker format
                        threats.append({
                            'ioc': line.strip(),
                            'type': 'ip',
                            'source': 'feodotracker',
                            'malware': 'Feodo'
                        })
                    elif 'urlhaus' in name:
                        # URLhaus format
                        if len(parts) >= 8:
                            threats.append({
                                'ioc': parts[2].strip(),
                                'type': 'url',
                                'malware': parts[6].strip(),
                                'source': 'urlhaus',
                                'status': parts[5].strip()
                            })
        
        elif 'blocklist' in name:
            # Text format - one IP per line
            for line in content.strip().split('\n'):
                if line and not line.startswith('#'):
                    threats.append({
                        'ioc': line.strip(),
                        'type': 'ip',
                        'source': 'blocklist_de',
                        'threat_type': 'ssh_bruteforce'
                    })
        
        elif 'phishtank' in name:
            # JSON format
            try:
                data = json.loads(content)
                for entry in data[:50]:  # First 50 entries
                    threats.append({
                        'ioc': entry.get('url', ''),
                        'type': 'url',
                        'source': 'phishtank',
                        'verified': entry.get('verified', ''),
                        'phish_detail_url': entry.get('phish_detail_url', '')
                    })
            except:
                pass
        
        print(f"  ✅ {name}: {len(threats)} threats")
        return threats
    
    async def fetch_all_feeds(self):
        """Fetch all feeds concurrently"""
        print("📡 Fetching threat feeds...")
        
        tasks = []
        for name, url in self.feeds.items():
            tasks.append(self.fetch_feed(name, url))
        
        results = await asyncio.gather(*tasks)
        
        # Combine all results
        all_threats = []
        for result in results:
            if result:
                all_threats.extend(result)
        
        print(f"\n📊 TOTAL: {len(all_threats)} threats collected")
        return all_threats
    
    def save_threats(self, threats):
        """Save threats to JSON file"""
        output_file = f"/opt/shadowcore/feeds/processed/threats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_threats': len(threats),
                'sources': list(set([t.get('source', 'unknown') for t in threats])),
                'threats': threats[:1000]  # First 1000 threats
            }, f, indent=2)
        
        print(f"💾 Saved to: {output_file}")
        return output_file
    
    async def integrate_with_shadowcore(self, threats_file):
        """Integrate with existing ShadowCore systems"""
        print("\n🔗 Integrating with ShadowCore...")
        
        # 1. Load the threats
        with open(threats_file) as f:
            data = json.load(f)
        
        # 2. Create simple Neo4j integration
        neo4j_threats = []
        for threat in data['threats'][:50]:  # First 50 for demo
            neo4j_threats.append(threat['ioc'])
        
        # 3. Create Cypher query file
        cypher_file = "/opt/shadowcore/feeds/processed/load_to_neo4j.cypher"
        with open(cypher_file, 'w') as f:
            f.write("// Load threats from feeds into Neo4j\n")
            for threat in data['threats'][:20]:
                if threat['type'] == 'ip':
                    f.write(f"""
MERGE (i:IOC {{value: "{threat['ioc']}"}})
SET i.type = "ip",
    i.source = "{threat.get('source', 'unknown')}",
    i.threat_level = "high",
    i.first_seen = "{datetime.now().isoformat()}"
WITH i
MATCH (m:Malware {{name: "Cobalt Strike"}})
MERGE (i)-[:ASSOCIATED_WITH]->(m)
RETURN i.value as threat_ip, m.name as malware;
""")
        
        print(f"📝 Created Neo4j import script: {cypher_file}")
        print(f"📤 Ready to load {len(neo4j_threats)} threats into Neo4j")
        
        # 4. Create Redis cache file
        redis_file = "/opt/shadowcore/feeds/processed/redis_commands.txt"
        with open(redis_file, 'w') as f:
            for threat in data['threats'][:50]:
                key = f"threat:feed:{threat['ioc']}"
                f.write(f"HSET {key} ioc {threat['ioc']} type {threat['type']} source {threat.get('source', 'unknown')}\n")
                f.write(f"EXPIRE {key} 604800\n")  # 7 days
        
        print(f"🔐 Created Redis commands: {redis_file}")
        
        # 5. Update orchestrator cache
        cache_file = "/opt/shadowcore/feeds/processed/threat_cache.json"
        with open(cache_file, 'w') as f:
            # Create lookup dictionary
            cache_dict = {}
            for threat in data['threats']:
                cache_dict[threat['ioc']] = {
                    'threat_level': 'high',
                    'source': threat.get('source', 'unknown'),
                    'type': threat['type'],
                    'timestamp': datetime.now().isoformat()
                }
            json.dump(cache_dict, f, indent=2)
        
        print(f"📦 Threat cache created: {cache_file}")
        print(f"   {len(cache_dict)} threats ready for real-time lookup")
        
        return {
            'threats_file': threats_file,
            'cypher_file': cypher_file,
            'redis_file': redis_file,
            'cache_file': cache_file,
            'total_threats': len(data['threats'])
        }

async def main():
    """Main function"""
    print("🎯 Starting ShadowCore Feed Integration")
    print("=" * 50)
    
    manager = SimpleFeedManager()
    
    # Step 1: Fetch threats
    threats = await manager.fetch_all_feeds()
    
    if not threats:
        print("❌ No threats collected. Check network connectivity.")
        return
    
    # Step 2: Save threats
    threats_file = manager.save_threats(threats)
    
    # Step 3: Integrate with ShadowCore
    results = await manager.integrate_with_shadowcore(threats_file)
    
    print("\n" + "=" * 50)
    print("✅ FEED INTEGRATION COMPLETE")
    print("=" * 50)
    print(f"📊 Threats Collected: {results['total_threats']}")
    print(f"📁 Files Created:")
    print(f"   • Threats: {results['threats_file']}")
    print(f"   • Neo4j Import: {results['cypher_file']}")
    print(f"   • Redis Cache: {results['redis_file']}")
    print(f"   • Real-time Cache: {results['cache_file']}")
    print("\n🚀 Next Steps:")
    print("1. Load threats to Neo4j: cat {} | cypher-shell -u neo4j -p Jonboy@123".format(results['cypher_file']))
    print("2. Load to Redis: cat {} | redis-cli".format(results['redis_file']))
    print("3. Use in orchestrator: Threat cache ready at {}".format(results['cache_file']))

if __name__ == "__main__":
    asyncio.run(main())
