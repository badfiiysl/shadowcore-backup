#!/usr/bin/env python3
"""
ShadowCore Health Monitor
Run: python3 shadowcore_health.py [--all] [--port PORT]
"""
import socket
import requests
import json
import sys
import argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Service definitions with expected type
SERVICES = {
    # Python Services
    'main_rest': {'host': '127.0.0.1', 'port': 8000, 'type': 'http', 'endpoint': '/health'},
    'threat_api': {'host': '127.0.0.1', 'port': 8003, 'type': 'http', 'endpoint': '/health'},
    'main_api': {'host': '127.0.0.1', 'port': 8004, 'type': 'http', 'endpoint': '/health'},
    'auth_api': {'host': '127.0.0.1', 'port': 8006, 'type': 'http', 'endpoint': '/health'},
    'proxy': {'host': '127.0.0.1', 'port': 8080, 'type': 'http', 'endpoint': '/health'},
    'websocket': {'host': '127.0.0.1', 'port': 8083, 'type': 'tcp'},
    'rpc': {'host': '127.0.0.1', 'port': 4242, 'type': 'tcp'},
    'dashboard': {'host': '127.0.0.1', 'port': 8010, 'type': 'http'},
    'ui_dashboard': {'host': '127.0.0.1', 'port': 8020, 'type': 'http'},
    'threat_intel': {'host': '127.0.0.1', 'port': 8090, 'type': 'http'},
    'threat_insight': {'host': '127.0.0.1', 'port': 9090, 'type': 'http'},
    
    # Node.js Services
    'shadowsearch': {'host': '127.0.0.1', 'port': 8002, 'type': 'http'},
    'shadowbrain': {'host': '127.0.0.1', 'port': 8001, 'type': 'http'},
    'electron': {'host': '127.0.0.1', 'port': 8082, 'type': 'http'},
    
    # Infrastructure
    'metrics': {'host': '127.0.0.1', 'port': 9100, 'type': 'http'},
    'ollama': {'host': '127.0.0.1', 'port': 11434, 'type': 'http'},
    'grafana': {'host': '127.0.0.1', 'port': 3000, 'type': 'http'},
    'postgres': {'host': '127.0.0.1', 'port': 5432, 'type': 'tcp'},
    'redis': {'host': '127.0.0.1', 'port': 6379, 'type': 'tcp'},
    'neo4j_http': {'host': '127.0.0.1', 'port': 7474, 'type': 'http'},
    'neo4j_bolt': {'host': '127.0.0.1', 'port': 7687, 'type': 'tcp'},
    'containerd': {'host': '127.0.0.1', 'port': 42001, 'type': 'tcp'},
}

def check_tcp(host, port, timeout=2):
    """Check TCP port connectivity"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def check_http(host, port, endpoint='/', timeout=2):
    """Check HTTP service health"""
    try:
        url = f"http://{host}:{port}{endpoint}"
        response = requests.get(url, timeout=timeout)
        return response.status_code < 500
    except Exception:
        return False

def check_service(name, config):
    """Check individual service"""
    host, port = config['host'], config['port']
    service_type = config.get('type', 'tcp')
    endpoint = config.get('endpoint', '/')
    
    try:
        if service_type == 'http':
            status = check_http(host, port, endpoint)
        else:
            status = check_tcp(host, port)
        
        return {
            'service': name,
            'host': host,
            'port': port,
            'type': service_type,
            'status': 'UP' if status else 'DOWN',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'service': name,
            'host': host,
            'port': port,
            'type': service_type,
            'status': 'ERROR',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

def check_all_services():
    """Check all services concurrently"""
    results = []
    print("🔍 Checking all ShadowCore services...")
    print("=" * 70)
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_service = {
            executor.submit(check_service, name, config): name 
            for name, config in SERVICES.items()
        }
        
        for future in as_completed(future_to_service):
            result = future.result()
            results.append(result)
    
    # Sort and display
    results.sort(key=lambda x: x['status'])
    
    up_count = sum(1 for r in results if r['status'] == 'UP')
    down_count = sum(1 for r in results if r['status'] == 'DOWN')
    
    # Display results
    for result in results:
        status_icon = '🟢' if result['status'] == 'UP' else '🔴'
        print(f"{status_icon} {result['service']:20} {result['host']}:{result['port']:5} [{result['type']:6}] → {result['status']}")
    
    print("=" * 70)
    print(f"📊 SUMMARY: {up_count} UP, {down_count} DOWN, {len(results) - up_count - down_count} ERRORS")
    
    # Save to file
    with open('/tmp/shadowcore_health.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Detailed results saved to: /tmp/shadowcore_health.json")
    
    return results

def check_single_port(port):
    """Check a specific port across all services"""
    print(f"🔍 Checking port {port}...")
    found = False
    for name, config in SERVICES.items():
        if config['port'] == port:
            found = True
            result = check_service(name, config)
            status_icon = '🟢' if result['status'] == 'UP' else '🔴'
            print(f"{status_icon} {result['service']:20} → {result['status']}")
            return result
    
    if not found:
        # Check any service on that port
        print(f"⚠️  No service defined for port {port}, testing connectivity...")
        if check_tcp('127.0.0.1', port):
            print(f"🟢 Port {port} is open but not in service map")
        else:
            print(f"🔴 Port {port} is closed")

def main():
    parser = argparse.ArgumentParser(description='ShadowCore Health Monitor')
    parser.add_argument('--all', action='store_true', help='Check all services')
    parser.add_argument('--port', type=int, help='Check specific port')
    parser.add_argument('--export', action='store_true', help='Export to JSON')
    
    args = parser.parse_args()
    
    if args.port:
        check_single_port(args.port)
    elif args.all:
        check_all_services()
    else:
        # Quick check of critical services
        critical = ['main_rest', 'auth_api', 'postgres', 'redis', 'proxy']
        print("🚀 Quick health check for critical services...")
        print("=" * 50)
        for service in critical:
            if service in SERVICES:
                result = check_service(service, SERVICES[service])
                status_icon = '🟢' if result['status'] == 'UP' else '🔴'
                print(f"{status_icon} {result['service']:20} → {result['status']}")

if __name__ == "__main__":
    main()
