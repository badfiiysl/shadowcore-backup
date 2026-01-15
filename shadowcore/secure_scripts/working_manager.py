#!/usr/bin/env python3
"""
Working ShadowCore Manager - Uses actual running processes
"""
import os
import sys
import time
import signal
import subprocess
import json
from datetime import datetime

def get_running_services():
    """Get actually running shadowcore services"""
    services = []
    
    # Get process info using ps
    ps_cmd = "ps aux | grep -E '(python.*shadow|node.*shadow)' | grep -v grep"
    result = subprocess.run(ps_cmd, shell=True, capture_output=True, text=True)
    
    for line in result.stdout.strip().split('\n'):
        if not line:
            continue
        
        parts = line.split()
        pid = parts[1]
        cmd = ' '.join(parts[10:])
        
        # Determine service type and port
        service = {
            'pid': pid,
            'cmd': cmd,
            'type': 'python' if 'python' in cmd.lower() else 'node',
            'name': 'Unknown',
            'port': None
        }
        
        # Extract name and port
        if 'launch_rest.py' in cmd:
            service['name'] = 'Main REST API'
            service['port'] = 8000
        elif 'simple_threat_api.py' in cmd:
            service['name'] = 'Threat API'
            service['port'] = 8003
        elif 'simple_main_api.py' in cmd:
            service['name'] = 'Main API'
            service['port'] = 8004
        elif 'production_auth.py' in cmd:
            service['name'] = 'Auth API'
            service['port'] = 8006
        elif 'real_proxy.py' in cmd:
            service['name'] = 'Proxy'
            service['port'] = 8080
        elif 'websocket_production.py' in cmd:
            service['name'] = 'WebSocket'
            service['port'] = 8083
        elif 'rpc/server.py' in cmd:
            service['name'] = 'RPC Server'
            service['port'] = 4242
        elif 'dashboard.py' in cmd:
            service['name'] = 'UI Dashboard'
            service['port'] = 8020
        elif 'threat-insight-api.py' in cmd:
            service['name'] = 'Threat Insight'
            service['port'] = 9090
        elif 'pure-server.js' in cmd:
            service['name'] = 'Electron Server'
            service['port'] = 8082
        elif 'working-api.js' in cmd:
            service['name'] = 'ShadowBrain API'
            service['port'] = 8001
        elif 'simple_8002.js' in cmd:
            service['name'] = 'ShadowSearch'
            service['port'] = 8002
        
        services.append(service)
    
    return services

def check_port(port):
    """Check if port is open"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            return s.connect_ex(('127.0.0.1', port)) == 0
    except:
        return False

def display_services(services):
    """Display services in a nice format"""
    print(f"\n{'PID':<8} {'PORT':<6} {'STATUS':<8} {'SERVICE':<25} {'TYPE':<8}")
    print("-" * 70)
    
    for svc in services:
        status = "🟢 OPEN" if svc['port'] and check_port(svc['port']) else "🟡 SLEEP"
        print(f"{svc['pid']:<8} {svc['port'] or 'N/A':<6} {status:<8} {svc['name']:<25} {svc['type']:<8}")

def restart_service(service):
    """Restart a specific service"""
    print(f"\n🔄 Restarting {service['name']}...")
    
    # Kill existing process
    try:
        os.kill(int(service['pid']), signal.SIGTERM)
        time.sleep(2)
    except:
        pass
    
    # Extract command to restart
    cmd_parts = service['cmd'].split()
    
    # Remove PID and other ps artifacts
    if cmd_parts[0].endswith('python') or cmd_parts[0].endswith('python3'):
        # Python service
        script_idx = next((i for i, part in enumerate(cmd_parts) if part.endswith('.py')), -1)
        if script_idx != -1:
            script = cmd_parts[script_idx]
            args = cmd_parts[script_idx+1:] if script_idx+1 < len(cmd_parts) else []
            
            # Reconstruct command
            new_cmd = ['python3', script] + args
            print(f"   Starting: {' '.join(new_cmd)}")
            
            # Start in background
            with open(f"/tmp/{service['name'].replace(' ', '_')}.log", 'w') as f:
                subprocess.Popen(new_cmd, stdout=f, stderr=subprocess.STDOUT)
    
    elif cmd_parts[0].endswith('node'):
        # Node.js service
        script_idx = next((i for i, part in enumerate(cmd_parts) if part.endswith('.js')), -1)
        if script_idx != -1:
            script = cmd_parts[script_idx]
            new_cmd = ['node', script]
            print(f"   Starting: {' '.join(new_cmd)}")
            
            with open(f"/tmp/{service['name'].replace(' ', '_')}.log", 'w') as f:
                subprocess.Popen(new_cmd, stdout=f, stderr=subprocess.STDOUT)
    
    time.sleep(3)
    print(f"   ✅ {service['name']} restart initiated")

def main():
    print("🛠️ ShadowCore Working Manager")
    print("=" * 60)
    
    while True:
        services = get_running_services()
        
        print(f"\n📊 {len(services)} services running")
        display_services(services)
        
        print("\n🔧 Commands:")
        print("   [r] Refresh view")
        print("   [a] Restart all services")
        print("   [1-9] Restart service by number")
        print("   [q] Quit")
        
        choice = input("\nSelect: ").strip().lower()
        
        if choice == 'q':
            break
        elif choice == 'r':
            continue
        elif choice == 'a':
            print("\n🔄 Restarting all services...")
            for svc in services:
                restart_service(svc)
                time.sleep(2)
            print("\n✅ All services restart initiated")
            time.sleep(5)
        elif choice.isdigit() and 1 <= int(choice) <= len(services):
            idx = int(choice) - 1
            restart_service(services[idx])
            time.sleep(3)

if __name__ == "__main__":
    main()
