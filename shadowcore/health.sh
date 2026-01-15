#!/bin/bash
echo "🩺 ShadowCore Health Check"
ports=(8000 8003 8004 8006 8080 8083 8020 9090 8002 8001 8082)
for port in "${ports[@]}"; do
    if timeout 1 bash -c "echo > /dev/tcp/127.0.0.1/$port" 2>/dev/null; then
        echo "🟢 Port $port: OPEN"
    else
        echo "🔴 Port $port: CLOSED"
    fi
done
