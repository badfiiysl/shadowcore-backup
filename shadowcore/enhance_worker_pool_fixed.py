#!/usr/bin/env python3
"""
Enhanced Worker Pool - Fixed Version
"""

import asyncio
import aiohttp

class EnhancedWorkerPool:
    def __init__(self):
        self.workers = {
            "geo_lookup": self.geo_lookup_worker,
            "reputation_check": self.reputation_worker,
            "malware_analysis": self.malware_analysis_worker,
            "phishing_check": self.phishing_check_worker
        }
    
    async def geo_lookup_worker(self, ioc):
        """Geolocation lookup worker"""
        return {
            "worker": "geo_lookup",
            "country": "Unknown",
            "asn": "ASN Unknown",
            "provider": "Unknown ISP",
            "confidence": 0.5
        }
    
    async def reputation_worker(self, ioc):
        """Reputation check worker"""
        return {
            "worker": "reputation_check",
            "abuse_score": 75,
            "malicious_votes": 5,
            "confidence": 0.8,
            "sources": ["simulated_abuseipdb", "simulated_virustotal"]
        }
    
    async def malware_analysis_worker(self, ioc):
        """Malware analysis worker"""
        return {
            "worker": "malware_analysis",
            "detections": 15,
            "engines": 65,
            "first_seen": "2024-01-01",
            "tags": ["trojan", "backdoor", "c2"]
        }
    
    async def phishing_check_worker(self, ioc):
        """Phishing check worker"""
        return {
            "worker": "phishing_check",
            "is_phishing": True,
            "confidence": 0.85,
            "patterns": ["suspicious_domain", "typo_squatting"]
        }
    
    async def process_ioc(self, ioc, worker_types):
        """Process IOC with multiple workers"""
        results = {}
        
        for worker_type in worker_types:
            if worker_type in self.workers:
                try:
                    result = await self.workers[worker_type](ioc)
                    results[worker_type] = result
                except Exception as e:
                    results[worker_type] = {"error": str(e)}
        
        return results

# Test it
async def test():
    pool = EnhancedWorkerPool()
    
    # Test with different IOC types
    test_cases = [
        {"ioc": "23.95.44.80", "workers": ["geo_lookup", "reputation_check"]},
        {"ioc": "evil-traffic.com", "workers": ["phishing_check", "reputation_check"]},
        {"ioc": "abc123malwarehash", "workers": ["malware_analysis"]}
    ]
    
    print("✅ Enhanced Worker Pool - Fixed Version")
    print("="*50)
    
    for test in test_cases:
        print(f"\n🔍 Processing: {test['ioc']}")
        print(f"   Workers: {', '.join(test['workers'])}")
        
        results = await pool.process_ioc(test['ioc'], test['workers'])
        
        for worker, result in results.items():
            print(f"   {worker}: {result.get('confidence', 'N/A')} confidence")

asyncio.run(test())
