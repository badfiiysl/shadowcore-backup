#!/bin/bash
echo "✅ ShadowCore Working Health Check"
echo "=================================="

# Check core services
echo "Core Services Status:"
echo "-------------------"

check_service() {
    local port=$1
    local name=$2
    
    if timeout 1 bash -c "echo > /dev/tcp/127.0.0.1/$port" 2>/dev/null; then
        # Try HTTP check
        if curl -s --max-time 2 "http://127.0.0.1:$port" > /dev/null 2>&1; then
            echo "🟢 $name (:$port) - HTTP OK"
        elif curl -s --max-time 2 "http://127.0.0.1:$port/health" > /dev/null 2>&1; then
            echo "🟢 $name (:$port) - Health endpoint OK"
        else
            echo "🟡 $name (:$port) - TCP open, no HTTP"
        fi
        return 0
    else
        echo "🔴 $name (:$port) - CLOSED"
        return 1
    fi
}

# Check all ports
ports=(
    "8000:Main REST API"
    "8003:Threat API"
    "8004:Main API"
    "8006:Auth API"
    "8080:Proxy"
    "8083:WebSocket"
    "4242:RPC Server"
    "8020:UI Dashboard"
    "9090:Threat Insight"
    "8002:ShadowSearch"
    "8001:ShadowBrain API"
    "8082:Electron Server"
    "5432:PostgreSQL"
    "6379:Redis"
    "7474:Neo4j HTTP"
    "7687:Neo4j Bolt"
    "11434:Ollama"
    "3000:Grafana"
    "9100:Node Exporter"
    "42001:Containerd"
)

for entry in "${ports[@]}"; do
    port="${entry%%:*}"
    name="${entry#*:}"
    check_service "$port" "$name"
done

# Process summary
echo -e "\n📊 Process Summary:"
echo "-----------------"
python_count=$(ps aux | grep -c "[p]ython.*shadow")
node_count=$(ps aux | grep -c "[n]ode.*shadow")
echo "Python ShadowCore processes: $python_count"
echo "Node.js ShadowCore processes: $node_count"

# Check if services are actually responsive
echo -e "\n🧪 Quick Responsiveness Test:"
echo "----------------------------"
test_endpoint() {
    local url=$1
    local name=$2
    if curl -s --max-time 3 "$url" > /dev/null 2>&1; then
        echo "🟢 $name: Responsive"
    else
        echo "🔴 $name: Not responsive"
    fi
}

test_endpoint "http://127.0.0.1:8000" "Main API"
test_endpoint "http://127.0.0.1:8020" "UI Dashboard"
test_endpoint "http://127.0.0.1:8080" "Proxy"
test_endpoint "http://127.0.0.1:3000" "Grafana"
