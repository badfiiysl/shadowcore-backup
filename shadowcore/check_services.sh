#!/bin/bash
echo "🔍 SHADOWCORE SERVICE STATUS CHECK"
echo "================================="

# Check systemd services
echo -e "\n📦 SYSTEMD SERVICES:"
systemctl list-units --type=service | grep -E "(shadow|neo4j|redis|postgres|grafana)" | while read line; do
    service=$(echo $line | awk '{print $1}')
    status=$(echo $line | awk '{print $3}')
    if [ "$status" = "active" ]; then
        echo "✅ $service: ACTIVE"
    else
        echo "❌ $service: $status"
    fi
done

# Check network services
echo -e "\n🌐 NETWORK SERVICES:"
declare -A services=(
    [8000]="REST API"
    [8002]="ShadowSearch"
    [8003]="Threat API"
    [8004]="Main API"
    [8006]="Auth API"
    [8020]="Dashboard"
    [3000]="Grafana"
    [7474]="Neo4j Browser"
    [7687]="Neo4j Bolt"
    [6379]="Redis"
    [5432]="PostgreSQL"
    [11434]="Ollama"
)

for port in "${!services[@]}"; do
    if netstat -tln | grep ":$port " > /dev/null; then
        echo "✅ Port $port (${services[$port]}): LISTENING"
    else
        echo "❌ Port $port (${services[$port]}): NOT LISTENING"
    fi
done

# Check main processes
echo -e "\n⚙️  MAIN PROCESSES:"
if pgrep -f "shadowcore" > /dev/null; then
    echo "✅ ShadowCore process: RUNNING"
else
    echo "❌ ShadowCore process: NOT RUNNING"
fi

if pgrep -f "neo4j" > /dev/null; then
    echo "✅ Neo4j process: RUNNING"
else
    echo "❌ Neo4j process: NOT RUNNING"
fi

if pgrep -f "redis" > /dev/null; then
    echo "✅ Redis process: RUNNING"
else
    echo "❌ Redis process: NOT RUNNING"
fi
