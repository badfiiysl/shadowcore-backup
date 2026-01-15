#!/usr/bin/env python3
"""
Inject health endpoints into ShadowCore services
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
        'timestamp': '{timestamp_placeholder}'
    }, 200

@app.route('/health/detailed')
def detailed_health():
    import psutil
    import datetime
    process = psutil.Process()
    return {
        'status': 'healthy',
        'service': '{service_name}',
        'pid': process.pid,
        'memory_mb': process.memory_info().rss / 1024 / 1024,
        'cpu_percent': process.cpu_percent(interval=0.1),
        'uptime': str(datetime.datetime.now() - datetime.datetime.fromtimestamp(process.create_time())),
        'connections': len(process.connections()),
        'timestamp': datetime.datetime.now().isoformat()
    }, 200
"""

def inject_into_python_file(filepath, service_name):
    """Inject health endpoints into Python Flask/FastAPI app"""
    if not os.path.exists(filepath):
        print(f"⚠️  File not found: {filepath}")
        return False
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check if already has health endpoint
    if '/health' in content and 'def health' in content:
        print(f"✓ {service_name}: Health endpoint already exists")
        return True
    
    # Find where to inject (after app definition)
    lines = content.split('\n')
    injection_point = -1
    
    for i, line in enumerate(lines):
        if 'app = Flask' in line or 'app = FastAPI' in line or 'app.route' in line:
            injection_point = i + 1
            break
    
    if injection_point == -1:
        # Try to find any @app.route
        for i, line in enumerate(lines):
            if '@app' in line:
                injection_point = i
                break
    
    if injection_point == -1:
        print(f"⚠️  {service_name}: Could not find injection point")
        return False
    
    # Prepare injection code
    health_code = HEALTH_ENDPOINT_CODE.replace('{service_name}', service_name)
    
    # Insert the code
    lines.insert(injection_point, health_code)
    
    # Write back
    with open(filepath, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✓ {service_name}: Health endpoint injected")
    return True

def inject_into_node_file(filepath, service_name):
    """Inject health endpoint into Node.js Express app"""
    if not os.path.exists(filepath):
        print(f"⚠️  File not found: {filepath}")
        return False
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check if already has health endpoint
    if 'app.get(\'/health' in content:
        print(f"✓ {service_name}: Health endpoint already exists")
        return True
    
    # Node.js health endpoint code
    node_health_code = """
// Health endpoints
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        service: '%s',
        timestamp: new Date().toISOString()
    });
});

app.get('/health/detailed', (req, res) => {
    const memoryUsage = process.memoryUsage();
    res.json({
        status: 'healthy',
        service: '%s',
        pid: process.pid,
        memory_mb: memoryUsage.rss / 1024 / 1024,
        uptime: process.uptime(),
        timestamp: new Date().toISOString()
    });
});
""" % (service_name, service_name)
    
    # Find injection point (after app/express definition)
    if 'app.get(' in content:
        # Insert before the first route
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'app.get(' in line or 'app.post(' in line:
                lines.insert(i, node_health_code)
                break
        else:
            lines.append(node_health_code)
        
        with open(filepath, 'w') as f:
            f.write('\n'.join(lines))
    else:
        # Append at the end
        with open(filepath, 'a') as f:
            f.write('\n' + node_health_code)
    
    print(f"✓ {service_name}: Health endpoint injected")
    return True

def main():
    print("🩺 Injecting health endpoints into ShadowCore services...")
    print("="*60)
    
    services = [
        # Python services
        ('/opt/shadowcore-backend/launch_rest.py', 'python', 'Main REST API'),
        ('/opt/shadowcore-backend/simple_threat_api.py', 'python', 'Threat API'),
        ('/opt/shadowcore-backend/simple_main_api.py', 'python', 'Main API'),
        ('/opt/shadowcore-auth/production_auth.py', 'python', 'Auth API'),
        ('/opt/shadowcore/real_proxy.py', 'python', 'Proxy'),
        ('/opt/shadowcore/websocket_production.py', 'python', 'WebSocket'),
        ('/opt/shadowcore-backend/rpc/server.py', 'python', 'RPC Server'),
        ('/opt/shadowcore/ui/dashboard.py', 'python', 'UI Dashboard'),
        ('/opt/threat-insight/threat-insight-api.py', 'python', 'Threat Insight'),
        
        # Node.js services
        ('/opt/shadowsearch/simple_8002.js', 'node', 'ShadowSearch'),
        ('/opt/shadowbrain/working-api.js', 'node', 'ShadowBrain'),
        ('/root/shadowcore-electron/pure-server.js', 'node', 'Electron Server'),
    ]
    
    success_count = 0
    for filepath, lang, name in services:
        try:
            if lang == 'python':
                if inject_into_python_file(filepath, name):
                    success_count += 1
            elif lang == 'node':
                if inject_into_node_file(filepath, name):
                    success_count += 1
        except Exception as e:
            print(f"✗ {name}: Error - {e}")
    
    print("="*60)
    print(f"✅ Completed: {success_count}/{len(services)} services updated")
    print("\n🔄 Restart services to apply changes:")
    print("   sudo pkill -f 'python.*shadowcore'")
    print("   sudo pkill -f 'node.*shadow'")
    print("   Then restart with: /tmp/shadowcore_start.sh all")

if __name__ == "__main__":
    main()
