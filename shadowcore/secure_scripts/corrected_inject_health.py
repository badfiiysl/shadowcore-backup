#!/usr/bin/env python3
"""
Inject health endpoints with CORRECT paths
"""
import os
import sys
import re

HEALTH_ENDPOINT_CODE = """
@app.route('/health')
def health_check():
    return {
        'status': 'healthy',
        'service': '{service_name}',
        'timestamp': '__TIMESTAMP__'
    }, 200

@app.route('/health/detailed')
def detailed_health():
    import psutil
    import datetime
    import os
    process = psutil.Process(os.getpid())
    return {
        'status': 'healthy',
        'service': '{service_name}',
        'pid': process.pid,
        'memory_mb': round(process.memory_info().rss / 1024 / 1024, 2),
        'cpu_percent': process.cpu_percent(interval=0.1),
        'uptime': str(datetime.datetime.now() - datetime.datetime.fromtimestamp(process.create_time())),
        'timestamp': datetime.datetime.now().isoformat()
    }, 200
"""

def inject_into_file(filepath, service_name):
    """Inject health endpoints into Python file"""
    if not os.path.exists(filepath):
        print(f"⚠️  File not found: {filepath}")
        return False
    
    print(f"📝 Processing: {filepath}")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check if already has health endpoint
    if re.search(r'@app\.route\([\'"]/health[\'"]\)', content):
        print(f"   ✓ Already has health endpoint")
        return True
    
    # Check what framework is being used
    is_flask = 'Flask' in content or 'from flask' in content
    is_fastapi = 'FastAPI' in content or 'from fastapi' in content
    
    if not is_flask and not is_fastapi:
        print(f"   ⚠️  Not a Flask/FastAPI app, skipping")
        return False
    
    # Find the right place to inject (after imports and app definition)
    lines = content.split('\n')
    
    # Try to find after app definition
    injection_point = -1
    for i, line in enumerate(lines):
        if 'app = Flask' in line or 'app = FastAPI' in line:
            injection_point = i + 1
            break
    
    # If not found, try after last import
    if injection_point == -1:
        in_imports = True
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith(('import ', 'from ', '#', '"""')):
                if in_imports:
                    injection_point = i
                    break
    
    if injection_point == -1:
        injection_point = len(lines) - 1
    
    # Prepare health code
    health_code = HEALTH_ENDPOINT_CODE.replace('{service_name}', service_name)
    
    # Insert
    lines.insert(injection_point, health_code)
    
    # Write back
    with open(filepath, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"   ✅ Health endpoints injected")
    return True

def main():
    print("🎯 Injecting Health Endpoints (Corrected Paths)")
    print("=" * 60)
    
    # CORRECT PATHS from your system scan
    services = [
        # Python services (from ps output)
        ('/opt/shadowcore-backend/launch_rest.py', 'Main REST API'),
        ('/opt/shadowcore-backend/simple_threat_api.py', 'Threat API'),
        ('/opt/shadowcore-backend/simple_main_api.py', 'Main API'),
        ('/opt/shadowcore-auth/production_auth.py', 'Auth API'),
        ('/opt/shadowcore/real_proxy.py', 'Proxy'),
        ('/opt/shadowcore/websocket_production.py', 'WebSocket'),
        ('/opt/shadowcore-backend/rpc/server.py', 'RPC Server'),
        ('/opt/shadowcore/ui/dashboard.py', 'UI Dashboard'),
        ('/opt/threat-insight/threat-insight-api.py', 'Threat Insight'),
        
        # Found in /root
        ('/root/shadowcore_proxy.py', 'Root Proxy'),
        ('/root/mock_shadowsearch.py', 'Mock ShadowSearch'),
        ('/root/shadowcore_bridge_api.py', 'Bridge API'),
    ]
    
    success = 0
    for filepath, name in services:
        if inject_into_file(filepath, name):
            success += 1
    
    print("=" * 60)
    print(f"✅ Completed: {success}/{len(services)} services processed")
    
    # Check Node.js services
    print("\n🔍 Node.js Services found:")
    node_services = [
        ('/root/shadowcore-electron/pure-server.js', 'Electron Server'),
        ('/opt/shadowbrain/working-api.js', 'ShadowBrain API'),
    ]
    
    for filepath, name in node_services:
        if os.path.exists(filepath):
            print(f"📁 {name}: {filepath}")
            # Check if has health endpoint
            with open(filepath, 'r') as f:
                content = f.read()
                if 'app.get(\'/health' in content or 'app.get("/health' in content:
                    print(f"   ✓ Already has health endpoint")
                else:
                    print(f"   ⚠️  Needs health endpoint")
        else:
            print(f"⚠️  Not found: {filepath}")
    
    print("\n🚀 To apply changes, restart services:")
    print("   /tmp/quick_restart.sh")

if __name__ == "__main__":
    main()
