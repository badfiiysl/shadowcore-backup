#!/bin/bash
echo "🔧 FINAL 403 FIX SCRIPT"
echo "======================="

# 1. Show current config
echo "📋 Current config (first 15 lines):"
sudo head -15 /etc/nginx/sites-available/shadowcore

# 2. Check for root directive
echo -n "🔍 Root directive: "
if sudo grep -q "root " /etc/nginx/sites-available/shadowcore; then
    echo "✅ Found"
    sudo grep "root " /etc/nginx/sites-available/shadowcore
else
    echo "❌ MISSING - Adding it..."
    # Add root after server_name line
    sudo sed -i '/server_name shadowcore/a\    root /var/www/html;' /etc/nginx/sites-available/shadowcore
fi

# 3. Check for index directive  
echo -n "🔍 Index directive: "
if sudo grep -q "index " /etc/nginx/sites-available/shadowcore; then
    echo "✅ Found"
else
    echo "⚠️  Missing (adding optional)"
    sudo sed -i '/root/a\    index index.html index.htm;' /etc/nginx/sites-available/shadowcore
fi

# 4. Test and reload
echo "🧪 Testing config..."
sudo nginx -t
if [ $? -eq 0 ]; then
    echo "🔄 Reloading Nginx..."
    sudo systemctl reload nginx
    sleep 2
    
    # Test
    echo "🌐 Testing HTTPS..."
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://shadowcore.club/health --connect-timeout 5)
    echo "HTTP Code: $HTTP_CODE"
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "🎉 HTTPS WORKING!"
        curl -s https://shadowcore.club/health | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'Response: {d}')"
    elif [ "$HTTP_CODE" = "403" ]; then
        echo "❌ Still 403 - Checking permissions..."
        sudo tail -3 /var/log/nginx/error.log
    else
        echo "⚠️  Got code: $HTTP_CODE"
    fi
else
    echo "❌ Config test failed"
fi
