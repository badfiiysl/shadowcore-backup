#!/bin/bash
# Final ShadowCore Orchestrator Runner

echo "🧠 SHADOWCORE FINAL ORCHESTRATOR"
echo "========================================"
echo ""
echo "Your complete vision:"
echo "  👔 Agent Manager (schedules, ACL)"
echo "  👷 Worker Pool (workers, crawlers, parsers)"
echo "  🤖 AI Engines (cognitive + embed)"
echo "  📡 OSINT Engine (ingest feeds)"
echo "  🗄️  Memory (remembers, stores, correlates, maps)"
echo ""
echo "Starting orchestrator..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found!"
    exit 1
fi

# Run the orchestrator
cd /opt/shadowcore
python3 final_orchestrator.py

echo ""
echo "========================================"
echo "🏁 Orchestrator finished"
echo "Check reports in /opt/shadowcore/intelligence_reports/"
