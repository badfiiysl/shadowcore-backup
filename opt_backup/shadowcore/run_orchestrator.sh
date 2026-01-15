#!/bin/bash
# ShadowCore Orchestrator Runner

echo "🧠 STARTING SHADOWCORE ORCHESTRATOR"
echo "========================================"

# Check if orchestrator exists
if [ ! -f "/opt/shadowcore/orchestrator.py" ]; then
    echo "❌ Orchestrator not found!"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found!"
    exit 1
fi

echo "✅ Starting orchestrator..."
echo "   This will coordinate:"
echo "   • Agent Manager (Python APIs)"
echo "   • Worker Pool (WebSocket + workers)"
echo "   • AI Engines (shadowbrain + Ollama + Qdrant)"
echo "   • OSINT Engine (threat feeds)"
echo "   • Memory Systems (Neo4j, Redis, Postgres)"
echo ""
echo "📊 Output will be saved to /opt/shadowcore/reports/"
echo ""

# Run the orchestrator
cd /opt/shadowcore
python3 orchestrator.py

echo ""
echo "========================================"
echo "🏁 Orchestrator finished"
echo "Check reports in /opt/shadowcore/reports/"
