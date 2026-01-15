#!/bin/bash
echo "🔍 SHADOWCORE STATUS CHECK"
echo "=========================="

echo "1. Running processes:"
echo "-------------------"
ps aux | grep -E "(python|node).*shadow" | grep -v grep | while read line; do
    pid=$(echo $line | awk '{print $2}')
    cmd=$(echo $line | awk '{for(i=11;i<=NF;i++) printf $i" "; print ""}')
    echo "PID $pid: $cmd"
done

echo ""
echo "2. Port status:"
echo "--------------"
ports=(8000 8001 8002 8003 8004 8006 8080 8082 8083 8020 9090 4242 5432 6379 7474 7687 11434 3000 9100 42001)
for port in "${ports[@]}"; do
    if timeout 0.5 bash -c "echo > /dev/tcp/127.0.0.1/$port" 2>/dev/null; then
        echo "🟢 :$port"
    else
        echo "🔴 :$port"
    fi
done

echo ""
echo "3. Service tests:"
echo "----------------"
test_service() {
    echo -n "$1: "
    if curl -s --max-time 2 "http://127.0.0.1:$2" > /dev/null 2>&1; then
        echo "✅"
    else
        echo "❌"
    fi
}

test_service "Main REST API" 8000
test_service "Dashboard" 8020
test_service "Proxy" 8080
test_service "Grafana" 3000
test_service "PostgreSQL" 5432
test_service "Redis" 6379
test_service "Neo4j" 7474
test_service "Ollama" 11434

echo ""
echo "4. Quick curl to dashboard:"
curl -s http://127.0.0.1:8020 | grep -o "<title>.*</title>"
