#!/bin/bash
echo "📁 Actual Files in /root/projects/shadowcore"
echo "=========================================="

echo "Python files:"
find /root/projects/shadowcore -name "*.py" -type f | grep -v "__pycache__" | grep -v ".cipd_bin" | head -30

echo -e "\nNode.js files:"
find /root/projects/shadowcore -name "*.js" -type f | grep -v "node_modules" | head -10

echo -e "\nLooking for service files by content..."
grep -l "app\.route\|Flask\|FastAPI\|@app" /root/projects/shadowcore/*.py 2>/dev/null

echo -e "\nLooking for port numbers..."
grep -r "port.*=.*80\|PORT.*=.*80\|listen.*80" /root/projects/shadowcore/ --include="*.py" --include="*.js" 2>/dev/null | head -10
