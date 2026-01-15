#!/usr/bin/env python3
"""
Enhanced ShadowCore Health Monitor with detailed output
"""
import socket
import requests
import json
import psutil
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

SERVICES = {
    # Core APIs
    'main_rest': {'port': 8000, 'type': 'http', 'endpoint': '/health'},
    'threat_api': {'port': 8003, 'type': 'http', 'endpoint': '/health'},
    'main_api': {'port': 8004, 'type': 'http', 'endpoint': '/health'},
    'auth_api': {'port': 8006, 'type': 'http', 'endpoint': '/health'},
    'proxy': {'port': 8080, 'type': 'http', 'endpoint': '/health'},
    'websocket': {'port': 8083, 'type': 'tcp'},
    'rpc': {'port': 4242, 'type': 'tcp'},
    'ui_dashboard': {'port': 8020, 'type': 'http'},
    'threat_insight': {'port': 9090, 'type': 'http'},
    
    # Node.js Services
    'shadowsearch': {'port': 8002, 'type': 'http'},
    'shadowbrain': {'port': 8001, 'type': 'http'},
    'electron': {'port': 8082, 'type': 'http'},
    
    # Infrastructure
    'metrics': {'port': 9100, 'type': 'http'},
    'ollama': {'port': 11434, 'type': 'http'},
    'grafana': {'port': 3000, 'type': 'http'},
    'postgres': {'port': 5432, 'type': 'tcp'},
    'redis': {'port': 6379, 'type': 'tcp'},
    'neo4j_http': {'port': 7474, 'type': 'http'},
    'neo4j_bolt': {'port': 7687, 'type': 'tcp'},
    'containerd': {'port': 42001, 'type': 'tcp'},
}

def get_process_info(port):
    """Get process info for service running on port"""
    for conn in psutil.net_connections():
        if conn.laddr.port == port and conn.pid:
            try:
                p = psutil.Process(conn.pid)
                return {
                    'pid': conn.pid,
                    'name': p.name(),
                    'memory_mb': p.memory_info().rss / 1024 / 1024,
                    'cpu_percent': p.cpu_percent(interval=0.1),
                    'status': p.status()
                }
            except:
                return None
    return None

def check_service(name, config):
    """Enhanced service check with process info"""
    port = config['port']
    service_type = config.get('type', 'tcp')
    endpoint = config.get('endpoint', '/')
    
    result = {
        'service': name,
        'port': port,
        'type': service_type,
        'timestamp': datetime.now().isoformat()
    }
    
    # Check connectivity
    try:
        if service_type == 'http':
            url = f"http://127.0.0.1:{port}{endpoint}"
            response = requests.get(url, timeout=2)
            result['status'] = 'UP' if response.status_code < 500 else 'DOWN'
            if response.status_code < 500:
                try:
                    result['response_time'] = response.elapsed.total_seconds()
                    if response.content:
                        result['response'] = response.json()
                except:
                    pass
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            start = datetime.now()
            conn_result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            result['status'] = 'UP' if conn_result == 0 else 'DOWN'
            result['response_time'] = (datetime.now() - start).total_seconds()
    except Exception as e:
        result['status'] = 'ERROR'
        result['error'] = str(e)
    
    # Get process info
    proc_info = get_process_info(port)
    if proc_info:
        result.update(proc_info)
    
    return result

def display_results(results):
    """Display formatted results"""
    print("\n" + "="*90)
    print(f"{'SERVICE':<20} {'PORT':<6} {'STATUS':<8} {'PID':<8} {'MEM (MB)':<10} {'CPU %':<8} {'RESPONSE TIME'}")
    print("="*90)
    
    for r in results:
        status_color = '🟢' if r['status'] == 'UP' else '🔴' if r['status'] == 'DOWN' else '🟡'
        pid = r.get('pid', 'N/A')
        memory = f"{r.get('memory_mb', 0):.1f}" if 'memory_mb' in r else 'N/A'
        cpu = f"{r.get('cpu_percent', 0):.1f}" if 'cpu_percent' in r else 'N/A'
        response = f"{r.get('response_time', 0):.3f}s" if 'response_time' in r else 'N/A'
        
        print(f"{status_color} {r['service']:<18} {r['port']:<6} {r['status']:<8} {pid:<8} {memory:<10} {cpu:<8} {response}")

def main():
    print("🔍 ShadowCore Enhanced Health Check")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check all services concurrently
    results = []
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(check_service, name, config) 
                  for name, config in SERVICES.items()]
        
        for future in as_completed(futures):
            results.append(future.result())
    
    # Sort by status then service name
    results.sort(key=lambda x: (x['status'] != 'UP', x['service']))
    
    # Display
    display_results(results)
    
    # Summary
    up = sum(1 for r in results if r['status'] == 'UP')
    down = sum(1 for r in results if r['status'] == 'DOWN')
    error = sum(1 for r in results if r['status'] == 'ERROR')
    
    print("\n" + "="*90)
    print(f"📊 SUMMARY: {len(results)} services checked")
    print(f"   🟢 {up} UP | 🔴 {down} DOWN | 🟡 {error} ERRORS")
    
    # Save detailed report
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {'total': len(results), 'up': up, 'down': down, 'error': error},
        'services': results
    }
    
    report_file = '/tmp/shadowcore_detailed_report.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"💾 Detailed report saved: {report_file}")
    
    # Show critical ports that are down
    critical_ports = [5432, 6379, 8000, 8006]
    critical_down = []
    for r in results:
        if r['port'] in critical_ports and r['status'] != 'UP':
            critical_down.append(f"{r['service']} (port {r['port']})")
    
    if critical_down:
        print(f"\n⚠️  CRITICAL SERVICES DOWN: {', '.join(critical_down)}")

if __name__ == "__main__":
    main()
