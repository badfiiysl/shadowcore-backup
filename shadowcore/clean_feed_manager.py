#!/usr/bin/env python3
"""
CLEAN ShadowCore Feed Manager - Properly parses threat feeds
"""
import json
import csv
import asyncio
import aiohttp
from datetime import datetime
import os
import re
import sys

print("🧹 CLEAN SHADOWCORE FEED MANAGER")
print("=" * 50)

class CleanFeedManager:
    def __init__(self):
        self.feeds = {
            'feodo': {
                'url': 'https://feodotracker.abuse.ch/downloads/ipblocklist.csv',
                'parser': self.parse_feodo_csv
            },
            'blocklist_de': {
                'url': 'https://lists.blocklist.de/lists/all.txt',
                'parser': self.parse_blocklist_txt
            },
            'urlhaus': {
                'url': 'https://urlhaus.abuse.ch/downloads/csv_recent/',
                'parser': self.parse_urlhaus_csv
            },
            'sslbl': {
                'url': 'https://sslbl.abuse.ch/blacklist/sslblacklist.csv',
                'parser': self.parse_sslbl_csv
            }
        }
        
        # Create output directory
        os.makedirs('/opt/shadowcore/feeds/clean', exist_ok=True)
    
    def is_valid_ip(self, ip):
        """Validate IP address"""
        ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        if not re.match(ip_pattern, ip):
            return False
        
        # Check each octet
        parts = ip.split('.')
        for part in parts:
            if not 0 <= int(part) <= 255:
                return False
        return True
    
    async def parse_feodo_csv(self, content):
        """Parse Feodo Tracker CSV properly"""
        threats = []
        lines = content.strip().split('\n')
        
        for line in lines:
            if line.startswith('#') or not line.strip():
                continue
            
            # Feodo CSV format: first_seen,dst_ip,dst_port,c2_status,last_online,malware
            parts = line.split(',')
            if len(parts) >= 6:
                ip = parts[1].strip().strip('"')
                if self.is_valid_ip(ip):
                    threats.append({
                        'ioc': ip,
                        'type': 'ip',
                        'source': 'feodotracker',
                        'malware': parts[5].strip().strip('"'),
                        'port': parts[2].strip().strip('"'),
                        'first_seen': parts[0].strip().strip('"'),
                        'last_online': parts[4].strip().strip('"'),
                        'status': parts[3].strip().strip('"')
                    })
        
        return threats
    
    async def parse_blocklist_txt(self, content):
        """Parse Blocklist.de text file"""
        threats = []
        
        for line in content.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if self.is_valid_ip(line):
                threats.append({
                    'ioc': line,
                    'type': 'ip',
                    'source': 'blocklist_de',
                    'threat_type': 'ssh_bruteforce'
                })
        
        return threats
    
    async def parse_urlhaus_csv(self, content):
        """Parse URLhaus CSV"""
        threats = []
        lines = content.strip().split('\n')
        
        for i, line in enumerate(lines):
            if i == 0 or line.startswith('#') or not line.strip():
                continue  # Skip header
            
            parts = line.split(',')
            if len(parts) >= 9:
                url = parts[2].strip().strip('"')
                if url and url.startswith('http'):
                    threats.append({
                        'ioc': url,
                        'type': 'url',
                        'source': 'urlhaus',
                        'malware': parts[6].strip().strip('"') if len(parts) > 6 else '',
                        'status': parts[5].strip().strip('"') if len(parts) > 5 else ''
                    })
        
        return threats
    
    async def parse_sslbl_csv(self, content):
        """Parse SSL Blacklist CSV"""
        threats = []
        lines = content.strip().split('\n')
        
        for i, line in enumerate(lines):
            if i == 0 or line.startswith('#') or not line.strip():
                continue
            
            parts = line.split(',')
            if len(parts) >= 5:
                ip = parts[1].strip().strip('"')
                if self.is_valid_ip(ip):
                    threats.append({
                        'ioc': ip,
                        'type': 'ip',
                        'source': 'sslbl',
                        'malware': parts[4].strip().strip('"') if len(parts) > 4 else '',
                        'port': parts[2].strip().strip('"'),
                        'first_seen': parts[0].strip().strip('"')
                    })
        
        return threats
    
    async def fetch_feed(self, name, feed_info):
        """Fetch and parse a single feed"""
        try:
            headers = {
                'User-Agent': 'ShadowCore Threat Intelligence/1.0'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(feed_info['url'], headers=headers, timeout=30) as response:
                    if response.status == 200:
                        content = await response.text()
                        threats = await feed_info['parser'](content)
                        print(f"  ✅ {name}: {len(threats)} clean threats")
                        return threats
                    else:
                        print(f"  ❌ {name}: HTTP {response.status}")
                        return []
        except Exception as e:
            print(f"  ❌ {name}: Error - {str(e)[:50]}")
            return []
    
    async def fetch_all_feeds(self):
        """Fetch all feeds concurrently"""
        print("📡 Fetching and CLEANING threat feeds...")
        
        tasks = []
        for name, feed_info in self.feeds.items():
            tasks.append(self.fetch_feed(name, feed_info))
        
        results = await asyncio.gather(*tasks)
        
        # Combine all results
        all_threats = []
        for result in results:
            if result:
                all_threats.extend(result)
        
        # Remove duplicates
        unique_threats = []
        seen_iocs = set()
        for threat in all_threats:
            if threat['ioc'] not in seen_iocs:
                seen_iocs.add(threat['ioc'])
                unique_threats.append(threat)
        
        print(f"\n📊 TOTAL CLEAN THREATS: {len(unique_threats)} (deduplicated)")
        return unique_threats
    
    def save_clean_threats(self, threats):
        """Save clean threats"""
        output_file = f"/opt/shadowcore/feeds/clean/clean_threats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_threats': len(threats),
                'sources': list(set([t.get('source', 'unknown') for t in threats])),
                'threats': threats
            }, f, indent=2)
        
        print(f"💾 Clean threats saved to: {output_file}")
        return output_file
    
    def create_cache(self, threats_file):
        """Create clean threat cache for orchestrator"""
        with open(threats_file) as f:
            data = json.load(f)
        
        # Create cache dictionary
        cache = {}
        for threat in data['threats']:
            cache[threat['ioc']] = {
                'type': threat['type'],
                'source': threat.get('source', 'unknown'),
                'threat_level': 'high',  # All from feeds are high
                'timestamp': datetime.now().isoformat()
            }
            
            # Add extra fields if present
            if 'malware' in threat:
                cache[threat['ioc']]['malware'] = threat['malware']
            if 'port' in threat:
                cache[threat['ioc']]['port'] = threat['port']
        
        cache_file = "/opt/shadowcore/feeds/clean/threat_cache_clean.json"
        with open(cache_file, 'w') as f:
            json.dump(cache, f, indent=2)
        
        print(f"📦 Clean cache created: {cache_file}")
        print(f"   {len(cache)} threats ready for real-time lookup")
        
        return cache_file

async def main():
    """Main function"""
    print("🎯 Starting CLEAN ShadowCore Feed Integration")
    print("=" * 50)
    
    manager = CleanFeedManager()
    
    # Step 1: Fetch and clean threats
    threats = await manager.fetch_all_feeds()
    
    if not threats:
        print("❌ No clean threats collected.")
        return
    
    # Step 2: Save clean threats
    threats_file = manager.save_clean_threats(threats)
    
    # Step 3: Create clean cache
    cache_file = manager.create_cache(threats_file)
    
    print("\n" + "=" * 50)
    print("✅ CLEAN FEED INTEGRATION COMPLETE")
    print("=" * 50)
    
    # Show sample threats
    print("\n🔍 Sample clean threats:")
    with open(threats_file) as f:
        data = json.load(f)
        for i, threat in enumerate(data['threats'][:5]):
            print(f"  {i+1}. {threat['ioc']} - {threat.get('source', 'unknown')} ({threat.get('malware', '')})")
    
    print(f"\n🚀 Next: Update orchestrator to use clean cache:")
    print(f"   cp {cache_file} /opt/shadowcore/feeds/processed/threat_cache.json")

if __name__ == "__main__":
    asyncio.run(main())
