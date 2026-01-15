#!/usr/bin/env python3
import json, sys, os
from datetime import datetime

with open(sys.argv[1], 'r') as f:
    data = json.load(f)

html = f'''
<!DOCTYPE html>
<html>
<head>
    <title>ShadowCore TST Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 40px; background: #0f172a; color: #e2e8f0; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: #1e293b; padding: 2rem; border-radius: 10px; margin-bottom: 2rem; }}
        .section {{ background: #1e293b; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; }}
        .test-result {{ display: flex; justify-content: space-between; padding: 0.5rem; border-bottom: 1px solid #334155; }}
        .passed {{ color: #10b981; }}
        .failed {{ color: #ef4444; }}
        .warning {{ color: #f59e0b; }}
        .summary {{ font-size: 1.2rem; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ShadowCore Technology Stack Test</h1>
            <p>Report generated: {data["timestamp"]}</p>
        </div>
        
        <div class="section">
            <h2>Executive Summary</h2>
            <p class="summary">Success Rate: {data["summary"]["success_rate"]}%</p>
            <p>Status: {data["summary"]["status"]}</p>
        </div>
'''

for section_name, section_data in data["summary"]["sections"].items():
    passed = section_data["passed"]
    total = section_data["tested"]
    percentage = (passed / total * 100) if total > 0 else 0
    
    html += f'''
        <div class="section">
            <h3>{section_name.replace('_', ' ').title()}</h3>
            <p>{passed}/{total} tests passed ({percentage:.1f}%)</p>
        </div>
    '''

html += '''
    </div>
</body>
</html>
'''

html_file = sys.argv[1].replace('.json', '.html')
with open(html_file, 'w') as f:
    f.write(html)
print(f"HTML report generated: {html_file}")
