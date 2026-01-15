#!/bin/bash
echo "🧠 SMART WATCHDOG SEARCH"
echo "========================"

# Search for scripts that might be killing shadowcore
echo "1. Looking for kill commands targeting shadowcore..."
SEARCH_DIRS="/root /home /opt /etc"
for dir in $SEARCH_DIRS; do
    find "$dir" -type f \( -name "*.sh" -o -name "*.py" \) ! -path "*/node_modules/*" 2>/dev/null | while read file; do
        if grep -q -E "pkill.*shadow|kill.*shadow|kill.*python.*shadow|kill.*node.*shadow" "$file" 2>/dev/null; then
            echo "🚨 FOUND: $file"
            echo "   Content:"
            grep -n -B2 -A2 -E "pkill.*shadow|kill.*shadow" "$file" | sed 's/^/   /'
            echo "   ---"
        fi
    done
done

echo -e "\n2. Looking for auto-restart scripts..."
for dir in $SEARCH_DIRS; do
    find "$dir" -type f \( -name "*auto*restart*" -o -name "*watchdog*" -o -name "*health*" \) ! -path "*/node_modules/*" 2>/dev/null | head -10
done

echo -e "\n3. Checking for any 'service manager' scripts..."
find /opt /root -type f -name "*.sh" ! -path "*/node_modules/*" 2>/dev/null | while read file; do
    if head -20 "$file" 2>/dev/null | grep -q -E "(shadowcore|8001|8002|8003|8004)"; then
        echo "📁 Found script managing shadowcore: $file"
    fi
done

echo -e "\n4. Checking PM2 ecosystem files..."
find /root /opt -name "ecosystem*.js" -o -name "pm2*.json" 2>/dev/null | while read file; do
    echo "PM2 config: $file"
    if grep -q -E "(restart|kill|max_restarts)" "$file" 2>/dev/null; then
        grep -E "(restart|kill|max_restarts)" "$file" | sed 's/^/   /'
    fi
done

echo -e "\n5. Last resort: Check all running scripts..."
ps aux | grep -E "\.sh$|\.py$" | grep -v "grep" | while read line; do
    echo "Running script: $line"
done
