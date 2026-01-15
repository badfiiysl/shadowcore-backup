#!/usr/bin/env python3
import os
import sys
import subprocess
import json

def run_cmd(cmd, desc=""):
    print(f"🚀 {desc}" if desc else "🚀 Running...")
    print(f"   $ {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Success")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()[:50]}...")
            return True, result.stdout
        else:
            print(f"❌ Failed code {result.returncode}")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()[:50]}...")
            return False, result.stderr
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, str(e)

def update_nginx():
    print("\n" + "="*60)
    print("🔧 STEP 1: Update Nginx with domain")
    print("="*60)
    
    config = "/etc/nginx/sites-available/shadowcore"
    run_cmd(f"sudo cp {config} {config}.backup", "Backup config")
    
    with open(config, 'r') as f:
        content = f.read()
    
    if "shadowcore.club" in content:
        print("✅ Domain already in config")
        return True
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('server_name'):
            current = line.split('server_name')[1].strip(';').strip()
            lines[i] = f"    server_name {current} shadowcore.club www.shadowcore.club;"
            print(f"📝 Updating line: {lines[i]}")
            break
    
    with open("/tmp/shadowcore_new.conf", 'w') as f:
        f.write('\n'.join(lines))
    
    success, _ = run_cmd(f"sudo cp /tmp/shadowcore_new.conf {config}", "Write new config")
    return success

def setup_ssl():
    print("\n" + "="*60)
    print("🔒 STEP 2: HTTPS/SSL Setup (Optional)")
    print("="*60)
    
    print("📦 Installing Certbot...")
    success, _ = run_cmd("sudo apt update && sudo apt install certbot python3-certbot-nginx -y", "Install Certbot")
    if not success:
        print("⚠️  Install failed, skipping SSL")
        return False
    
    print("\n🎫 Getting SSL cert...")
    success, _ = run_cmd("sudo certbot --nginx -d shadowcore.club -d www.shadowcore.club --non-interactive --agree-tos --email admin@shadowcore.club", "Get SSL cert")
    return success

def test_config():
    print("\n" + "="*60)
    print("🧪 STEP 3: Test Configuration")
    print("="*60)
    
    success, _ = run_cmd("sudo nginx -t", "Test Nginx syntax")
    if not success:
        print("❌ Nginx test failed!")
        return False
    
    success, _ = run_cmd("sudo systemctl restart nginx", "Restart Nginx")
    if not success:
        print("❌ Nginx restart failed!")
        return False
    
    print("\n🌐 Testing domain...")
    health_test = 'curl -s -H "Host: shadowcore.club" http://localhost/health'
    success, output = run_cmd(health_test, "Health check")
    
    if success and "healthy" in output:
        print("✅ Health check passed!")
        try:
            data = json.loads(output)
            print(f"   Status: {data.get('status', 'unknown')}")
        except:
            pass
    
    print("\n🎯 Testing Threat API...")
    api_test = 'curl -s -H "Host: shadowcore.club" "http://localhost/api/threat/analyze?ioc=8.8.8.8"'
    success, output = run_cmd(api_test, "Threat API")
    
    if success:
        try:
            data = json.loads(output)
            print(f"✅ API: {data.get('ioc', '?')} → {data.get('threat_level', '?')}")
        except:
            print("⚠️  API response weird")
    
    return True

def create_monitor():
    print("\n" + "="*60)
    print("📊 STEP 4: Create Monitor Script")
    print("="*60)
    
    monitor = '''#!/bin/bash
echo "🖥️  SHADOWCORE DOMAIN MONITOR"
echo "============================="
date
echo ""
echo "🌐 Service Status:"
for svc in shadowcore-react-ui shadowcore-threat-api nginx; do
    status=$(systemctl is-active $svc 2>/dev/null || echo "not-found")
    if [ "$status" = "active" ]; then
        echo "✅ $svc: ACTIVE"
    else
        echo "❌ $svc: $status"
    fi
done
echo ""
echo "🧪 Domain Test:"
curl -s -H "Host: shadowcore.club" http://localhost/health | python3 -c "
import json
try:
    data = json.load(sys.stdin)
    print('✅ Health:', data.get('status', '?'))
except:
    print('❌ Health failed')
"
'''
    
    path = "/opt/shadowcore/domain-monitor.sh"
    success, _ = run_cmd(f"echo '{monitor}' | sudo tee {path} > /dev/null", f"Create {path}")
    if success:
        run_cmd(f"sudo chmod +x {path}", "Make executable")
        print(f"📝 Run: sudo {path}")

def main():
    print("="*60)
    print("🚀 SHADOWCORE DOMAIN SETUP")
    print("="*60)
    print(f"IP: 65.109.114.23")
    print(f"Domain: shadowcore.club")
    print("="*60)
    
    if os.geteuid() != 0:
        print("❌ Run as root: sudo python3 /opt/shadowcore/domain_setup.py")
        sys.exit(1)
    
    if not update_nginx():
        print("❌ Nginx update failed!")
        sys.exit(1)
    
    print("\n" + "="*60)
    ssl = input("🔒 Setup HTTPS? (y/N): ").strip().lower()
    if ssl == 'y':
        setup_ssl()
    
    test_config()
    create_monitor()
    
    print("\n" + "="*60)
    print("🎉 DONE!")
    print("="*60)
    print("""
✅ Done:
   1. Nginx updated with shadowcore.club
   2. Tested config
   3. Monitor script created

⚠️  You still need:
   1. Add A record: shadowcore.club → 65.109.114.23
   2. Wait for DNS (5-60 mins)
   3. HTTPS: sudo certbot --nginx -d shadowcore.club

📊 Monitor: sudo /opt/shadowcore/domain-monitor.sh
""")

if __name__ == "__main__":
    main()
