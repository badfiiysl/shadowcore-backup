#!/bin/bash
echo "🛑 Stopping ShadowCore System..."
echo "Time: $(date)"

# Stop dashboard
pkill -f "http.server 8020"

echo "✅ ShadowCore stopped at $(date)"
