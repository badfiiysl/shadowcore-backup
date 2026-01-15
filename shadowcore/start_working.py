#!/usr/bin/env python3
"""
Start all ShadowCore services
"""
import subprocess
import time
import os
import sys

services = [
    {"name": "Dashboard", "dir": "ui", "cmd": ["python", "dashboard.py"], "port": 8020},
    {"name": "Proxy", "dir": "core", "cmd": ["python", "real_proxy.py"], "port": 8080},
    {"name": "Threat API", "dir": "backend", "cmd": ["python", "simple_threat_api.py", "--host", "127.0.0.1", "--port", "8003"], "port": 8003},
    {"name": "Main API", "dir": "backend", "cmd": ["python", "simple_main_api.py", "--host", "127.0.0.1", "--port", "8004"], "port": 8004},
    {"name": "Auth API", "dir": "auth", "cmd": ["python", "production_auth.py", "--host", "127.0.0.1", "--port", "8006"], "port": 8006},
    {"name": "WebSocket", "dir": "core", "cmd": ["python", "websocket_production.py"], "port": 8083},
    {"name": "Threat Insight", "dir": "threat-insight", "cmd": ["python", "threat-insight-api.py"], "port": 9090},
]

print("🚀 Starting ShadowCore services...")
processes = []

for service in services:
    try:
        os.chdir(service["dir"])
        print(f"Starting {service['name']} on port {service['port']}...")
        proc = subprocess.Popen(
            service["cmd"],
            stdout=open(f"../logs/{service['name'].lower().replace(' ', '_')}.log", "w"),
            stderr=subprocess.STDOUT
        )
        processes.append((service["name"], proc))
        os.chdir("..")
        time.sleep(1)
    except Exception as e:
        print(f"❌ Failed to start {service['name']}: {e}")

# Start Main REST API separately (needs rest module)
print("Starting Main REST API on port 8000...")
os.chdir("backend")
rest_proc = subprocess.Popen(
    ["python", "launch_rest.py", "--host", "0.0.0.0", "--port", "8000"],
    stdout=open("../logs/main_rest.log", "w"),
    stderr=subprocess.STDOUT
)
processes.append(("Main REST API", rest_proc))
os.chdir("..")

print(f"\n✅ Started {len(processes)} services")
print("Waiting 5 seconds for startup...")
time.sleep(5)

print("\n📊 Port Status:")
import socket
ports = [8000, 8003, 8004, 8006, 8080, 8083, 8020, 9090]
for port in ports:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('127.0.0.1', port))
    status = "🟢" if result == 0 else "🔴"
    print(f"{status} Port {port}")
    sock.close()

print("\n🏁 ShadowCore is running!")
print("Access:")
print(f"  Dashboard: http://YOUR_IP:8020")
print(f"  Main API:  http://YOUR_IP:8000")
print(f"  Proxy:     http://YOUR_IP:8080")
