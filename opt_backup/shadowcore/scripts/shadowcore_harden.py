#!/usr/bin/env python3
"""
ShadowCore Security Hardener
Run: sudo python3 shadowcore_harden.py
"""
import os
import subprocess
import shutil
import json
from pathlib import Path

def check_temp_files():
    """Move temporary services to persistent storage"""
    print("🔧 Fixing temporary service files...")
    temp_services = [
        '/tmp/dashboard_8010.py',
        '/tmp/threat_intel_simple.py'
    ]
    
    persistent_dir = '/opt/shadowcore/services'
    os.makedirs(persistent_dir, exist_ok=True)
    
    fixes = []
    for temp_svc in temp_services:
        if os.path.exists(temp_svc):
            new_path = os.path.join(persistent_dir, os.path.basename(temp_svc))
            shutil.move(temp_svc, new_path)
            # Update systemd service if exists
            svc_name = os.path.basename(temp_svc).replace('.py', '')
            update_systemd_service(svc_name, new_path)
            fixes.append(f"✓ Moved {temp_svc} → {new_path}")
        else:
            fixes.append(f"⚠️ Not found: {temp_svc}")
    
    return fixes

def update_systemd_service(service_name, new_path):
    """Update systemd service file with new path"""
    service_file = f"/etc/systemd/system/{service_name}.service"
    if os.path.exists(service_file):
        with open(service_file, 'r') as f:
            content = f.read()
        content = content.replace(f"/tmp/{service_name}.py", new_path)
        with open(service_file, 'w') as f:
            f.write(content)
        subprocess.run(['systemctl', 'daemon-reload'], check=False)

def create_service_config():
    """Generate unified service configuration"""
    config = {
        "ports": {
            "api_group": [8000, 8003, 8004, 8006],
            "ui_group": [8080, 8083, 8020],
            "internal": [4242, 8010, 8090, 9090],
            "nodejs": [8001, 8002, 8082],
            "infra": [9100, 11434, 3000, 5432, 6379, 7474, 7687, 42001]
        },
        "health_endpoints": {
            "main_api": "http://127.0.0.1:8000/health",
            "auth_api": "http://127.0.0.1:8006/health",
            "proxy": "http://127.0.0.1:8080/health",
            "dashboard": "http://127.0.0.1:8020/health"
        }
    }
    
    config_dir = '/etc/shadowcore'
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, 'service_config.json')
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    return [f"✓ Service config created: {config_path}"]

def main():
    print("🛡️ ShadowCore Security Hardening")
    print("=" * 50)
    
    all_fixes = []
    
    # Fix 1: Move temp files
    fixes = check_temp_files()
    all_fixes.extend(fixes)
    
    # Fix 2: Create service config
    fixes = create_service_config()
    all_fixes.extend(fixes)
    
    # Summary
    print("\n✅ COMPLETED FIXES:")
    for fix in all_fixes:
        print(f"  {fix}")
    
    print("\n🚀 NEXT STEPS:")
    print("1. Review moved service files in /opt/shadowcore/services/")
    print("2. Restart services: sudo systemctl restart shadowcore-*")
    print("3. Check config: cat /etc/shadowcore/service_config.json")

if __name__ == "__main__":
    main()
