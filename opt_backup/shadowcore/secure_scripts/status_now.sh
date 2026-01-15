#!/bin/bash
echo "📊 ShadowCore Status Snapshot"
echo "============================="
date

echo -e "\n🔍 Running Processes:"
echo "-------------------"
ps aux | grep -E "(python.*shadow|node.*shadow|shadowcore)" | grep -v grep | awk '{printf "%-8s %-50s\n", $2, $11" "$12" "$13" "$14" "$15}'

echo -e "\n🌐 Open Ports:"
echo "------------"
for port in 8000 8001 8002 8003 8004 8006 8080 8082 8083 8020 9090 4242 5432 6379 7474 7687 11434 3000 9100 42001; do
    if timeout 0.5 bash -c "echo > /dev/tcp/127.0.0.1/$port" 2>/dev/null; then
        service=""
        case $port in
            8000) service="Main REST API" ;;
            8001) service="ShadowBrain API" ;;
            8002) service="ShadowSearch" ;;
            8003) service="Threat API" ;;
            8004) service="Main API" ;;
            8006) service="Auth API" ;;
            8080) service="Proxy" ;;
            8082) service="Electron Server" ;;
            8083) service="WebSocket" ;;
            8020) service="UI Dashboard" ;;
            9090) service="Threat Insight" ;;
            4242) service="RPC Server" ;;
            5432) service="PostgreSQL" ;;
            6379) service="Redis" ;;
            7474) service="Neo4j HTTP" ;;
            7687) service="Neo4j Bolt" ;;
            11434) service="Ollama" ;;
            3000) service="Grafana" ;;
            9100) service="Node Exporter" ;;
            42001) service="Containerd" ;;
        esac
        echo "🟢 :$port - $service"
    else
        echo "🔴 :$port - CLOSED"
    fi
done

echo -e "\n📈 System Resources:"
echo "------------------"
echo "CPU: $(uptime | awk -F'load average:' '{print $2}')"
echo "Memory: $(free -h | awk '/^Mem:/ {print $3"/"$2 " ("$3/$2*100"%)"}')"
echo "Disk: $(df -h / | awk 'NR==2 {print $3"/"$2 " ("$5")"}')"

echo -e "\n📁 Recent Logs:"
echo "--------------"
find /var/log/shadowcore -name "*.log" -type f 2>/dev/null | head -3 | while read log; do
    echo "$log:"
    tail -2 "$log" 2>/dev/null
done

echo -e "\n✅ Quick Test:"
curl -s http://127.0.0.1:8000 > /dev/null && echo "🟢 Main API: OK" || echo "🔴 Main API: FAIL"
curl -s http://127.0.0.1:8020 > /dev/null && echo "🟢 UI Dashboard: OK" || echo "🔴 UI Dashboard: FAIL"
curl -s http://127.0.0.1:3000 > /dev/null && echo "🟢 Grafana: OK" || echo "🔴 Grafana: FAIL"
