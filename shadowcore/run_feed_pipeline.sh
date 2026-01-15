#!/bin/bash
echo "🚀 SHADOWCORE 5-LAYER FEED PIPELINE"
echo "========================================"

# 1. Refresh all feeds
echo "🔄 Refreshing threat intelligence feeds..."
python3 /opt/shadowcore/feed_manager.py

# 2. Update Neo4j dashboard
echo "📊 Updating knowledge graph..."
curl -X POST http://localhost:8004/api/threats/refresh

# 3. Generate daily intelligence brief
echo "📋 Generating intelligence brief..."
python3 -c "
import json
from datetime import datetime

# Load latest report
import glob
reports = glob.glob('/opt/shadowcore/intelligence_reports/*.json')
if reports:
    latest = max(reports, key=lambda x: x.split('_')[-1])
    with open(latest) as f:
        data = json.load(f)
    
    print(f'📅 Daily Threat Intelligence Brief - {datetime.now().strftime(\"%Y-%m-%d\")}')
    print('=' * 50)
    print(f'Total Threats: {data[\"summary\"][\"total_threats\"]}')
    print(f'High Confidence: {data[\"summary\"][\"high_confidence\"]}')
    print(f'Sources: {len(data[\"summary\"][\"sources\"])}')
    
    if data[\"sample_threats\"]:
        print('\n🔍 Top Threats:')
        for threat in data[\"sample_threats\"][:5]:
            print(f'  • {threat[\"ioc\"]} - {threat[\"threat_level\"]} ({threat[\"source\"]})')
"

# 4. Log completion
echo "✅ Feed pipeline completed at $(date)" | tee -a /var/log/shadowcore_feeds.log
