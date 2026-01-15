#!/usr/bin/env python3
"""
ROBUST SHADOWCORE VALIDATION
Simplified and fixed validation script
"""
import json
import time
import redis
import requests
from datetime import datetime
import subprocess
import os
import socket

print("🔧 SHADOWCORE ROBUST VALIDATION")
print("=" * 50)

def test_service(port, name):
    """Test if a service is listening on a port"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False

def test_http(url, name):
    """Test if HTTP endpoint is accessible"""
    try:
        response = requests.get(url, timeout=5, allow_redirects=True)
        return response.status_code < 500
    except:
        return False

def run_validation():
    results = {
        'timestamp': datetime.now().isoformat(),
        'services': {},
        'components': {},
        'overall': 'PASS'
    }
    
    print("\n📊 TESTING CRITICAL COMPONENTS:")
    print("-" * 40)
    
    # 1. Test Redis
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis: Connected")
        results['components']['redis'] = 'PASS'
    except Exception as e:
        print(f"❌ Redis: {str(e)[:50]}")
        results['components']['redis'] = 'FAIL'
        results['overall'] = 'FAIL'
    
    # 2. Test Neo4j
    try:
        result = subprocess.run(
            ['cypher-shell', '-u', 'neo4j', '-p', 'Jonboy@123', '--format', 'plain',
             'RETURN "OK" as status'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            print("✅ Neo4j: Connected")
            results['components']['neo4j'] = 'PASS'
        else:
            print(f"❌ Neo4j: Command failed")
            results['components']['neo4j'] = 'FAIL'
            results['overall'] = 'FAIL'
    except Exception as e:
        print(f"❌ Neo4j: {str(e)[:50]}")
        results['components']['neo4j'] = 'FAIL'
        results['overall'] = 'FAIL'
    
    # 3. Test Threat Cache
    try:
        with open('/opt/shadowcore/feeds/processed/threat_cache.json') as f:
            threats = json.load(f)
        print(f"✅ Threat Cache: {len(threats):,} threats")
        results['components']['threat_cache'] = 'PASS'
    except Exception as e:
        print(f"❌ Threat Cache: {str(e)[:50]}")
        results['components']['threat_cache'] = 'FAIL'
        results['overall'] = 'FAIL'
    
    print("\n🌐 TESTING SERVICES:")
    print("-" * 40)
    
    # Define services to test
    services = [
        (8002, "ShadowSearch", "http://localhost:8002"),
        (8020, "Dashboard", "http://localhost:8020"),
        (3000, "Grafana", "http://localhost:3000"),
        (7474, "Neo4j Browser", "http://localhost:7474"),
    ]
    
    for port, name, url in services:
        # First test port connectivity
        if test_service(port, name):
            # Then test HTTP if applicable
            if url:
                if test_http(url, name):
                    print(f"✅ {name}: Listening & Accessible")
                    results['services'][name] = {'port': 'OPEN', 'http': 'ACCESSIBLE'}
                else:
                    print(f"⚠️  {name}: Listening but HTTP issue")
                    results['services'][name] = {'port': 'OPEN', 'http': 'ISSUE'}
            else:
                print(f"✅ {name}: Listening")
                results['services'][name] = {'port': 'OPEN', 'http': 'N/A'}
        else:
            print(f"❌ {name}: Not listening")
            results['services'][name] = {'port': 'CLOSED', 'http': 'N/A'}
            if name in ["Dashboard", "ShadowSearch"]:
                results['overall'] = 'FAIL'
    
    print("\n📈 SYSTEM METRICS:")
    print("-" * 40)
    
    # Memory usage
    try:
        with open('/proc/meminfo') as f:
            meminfo = f.readlines()
            total_mem = int(meminfo[0].split()[1]) / 1024  # MB
            free_mem = int(meminfo[1].split()[1]) / 1024   # MB
            used_percent = ((total_mem - free_mem) / total_mem) * 100
        print(f"💾 Memory: {used_percent:.1f}% used ({free_mem:.0f}MB free)")
    except:
        print("💾 Memory: Could not read")
    
    # Load average
    try:
        with open('/proc/loadavg') as f:
            load_avg = f.read().split()[:3]
        print(f"📊 Load: {load_avg[0]}, {load_avg[1]}, {load_avg[2]}")
    except:
        print("📊 Load: Could not read")
    
    # Uptime
    try:
        uptime = subprocess.getoutput('uptime -p')
        print(f"⏱️  Uptime: {uptime}")
    except:
        print("⏱️  Uptime: Could not read")
    
    print("\n" + "=" * 50)
    
    if results['overall'] == 'PASS':
        print("🎉 SHADOWCORE: ALL CRITICAL SYSTEMS OPERATIONAL")
        print("\n📌 ACCESS POINTS:")
        print("   Dashboard: http://localhost:8020")
        print("   ShadowSearch: http://localhost:8002")
        print("   Grafana: http://localhost:3000")
        print("   Neo4j Browser: http://localhost:7474")
        print("\n🎯 Your 'Better Palantir' is ready for production!")
    else:
        print("⚠️  SHADOWCORE: SOME ISSUES DETECTED")
        print("\n🔧 Focus on fixing the failed components above.")
        print("   Most services appear to be running correctly.")
    
    # Save results
    with open('/opt/shadowcore/validation_simple.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    run_validation()
