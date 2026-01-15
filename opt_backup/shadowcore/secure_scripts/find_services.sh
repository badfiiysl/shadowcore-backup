#!/bin/bash
echo "🔍 Finding ShadowCore Service Locations"
echo "========================================"

# Find Python services
echo "Python processes:"
ps aux | grep "[p]ython" | grep -i shadow | awk '{print $11 " " $12 " " $13 " " $14 " " $15}' | head -20

echo -e "\nNode.js processes:"
ps aux | grep "[n]ode" | grep -i shadow | awk '{print $11 " " $12 " " $13 " " $14 " " $15}' | head -20

echo -e "\nChecking common directories:"
for dir in /opt /usr/local /root /home; do
    if [ -d "$dir" ]; then
        echo "=== $dir ==="
        find "$dir" -name "*shadow*" -type f \( -name "*.py" -o -name "*.js" \) 2>/dev/null | head -5
    fi
done

echo -e "\nListening ports:"
ss -tulpn | grep -E ":8000|:8001|:8002|:8003|:8004|:8006|:8080|:8082|:8083|:8020|:9090|:4242"
