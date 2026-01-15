#!/usr/bin/env python3
"""Test ShadowSearch connectivity"""
import requests

print("🔍 Testing ShadowSearch connectivity...")
url = "http://localhost:8002"

try:
    response = requests.get(url, timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 404:
        print("⚠️  ShadowSearch is running but returning 404")
        print("   This might mean:")
        print("   1. It needs a specific endpoint (like /search)")
        print("   2. The root path isn't configured")
        print("   3. It's a different type of service")
    
    # Try common endpoints
    endpoints = ["/health", "/search", "/api/v1/search", "/api/search", "/ui", "/static"]
    for endpoint in endpoints:
        try:
            r = requests.get(url + endpoint, timeout=3)
            print(f"  {endpoint}: HTTP {r.status_code}")
        except:
            print(f"  {endpoint}: Timeout/Error")
            
except Exception as e:
    print(f"❌ Error connecting to ShadowSearch: {e}")
