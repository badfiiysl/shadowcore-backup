#!/bin/bash
echo "🚀 Starting ShadowCore System..."
echo "Time: $(date)"

# Start all services
echo "1. Starting Neo4j..."
systemctl start neo4j
sleep 5

echo "2. Starting Redis..."
systemctl start redis-server
sleep 2

echo "3. Starting Dashboard..."
cd /opt/shadowcore && nohup python3 -m http.server 8020 > /var/log/shadowcore_dashboard.log 2>&1 &

echo "4. Initializing Threat Intelligence..."
cd /opt/shadowcore && python3 /opt/shadowcore/clean_feed_manager.py

echo "✅ ShadowCore started at $(date)"
echo "Dashboard: http://localhost:8020"
echo "Neo4j: http://localhost:7474"
echo "Reports: /opt/shadowcore/intelligence_reports/"
