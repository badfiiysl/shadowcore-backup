#!/bin/bash
echo "🔒 EMERGENCY HTTPS FIX"
echo "======================"

# 1. Check current config
echo "📋 Current Nginx config:"
sudo grep "listen" /etc/nginx/sites-available/shadowcore

# 2. Create proper SSL config
echo "🔧 Creating SSL config..."
sudo tee /etc/nginx/sites-available/shadowcore << 'CONFIG'
# HTTPS Server
server {
    listen 443 ssl;
    server_name shadowcore.club www.shadowcore.club;
    
    # SSL certs from Certbot
    ssl_certificate /etc/letsencrypt/live/shadowcore.club-0001/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/shadowcore.club-0001/privkey.pem;
    
    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Main UI
    location / {
        proxy_pass http://localhost:3002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Threat API
    location /api/threat/ {
        proxy_pass http://localhost:8003/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Health check
    location /health {
        return 200 '{"status":"https-ready","service":"shadowcore-ui","timestamp":"$time_iso8601"}';
        add_header Content-Type application/json;
        access_log off;
    }
}

# HTTP redirect to HTTPS
server {
    listen 80;
    server_name shadowcore.club www.shadowcore.club;
    return 301 https://$server_name$request_uri;
}
CONFIG

# 3. Test and reload
echo "🧪 Testing config..."
sudo nginx -t
if [ $? -eq 0 ]; then
    echo "✅ Config valid"
    echo "🔄 Reloading Nginx..."
    sudo systemctl reload nginx
    sleep 2
else
    echo "❌ Config invalid, restoring backup"
    if [ -f /etc/nginx/sites-available/shadowcore.backup ]; then
        sudo cp /etc/nginx/sites-available/shadowcore.backup /etc/nginx/sites-available/shadowcore
        sudo nginx -t && sudo systemctl reload nginx
    fi
    exit 1
fi

# 4. Verify HTTPS is working
echo "🔍 Verifying HTTPS..."
echo "Waiting 3 seconds..."
sleep 3

if curl -s -o /dev/null -w "%{http_code}" https://shadowcore.club/health --connect-timeout 5 | grep -q "200"; then
    echo "🎉 HTTPS IS WORKING!"
    echo ""
    echo "🔗 Access: https://shadowcore.club"
    echo "🛡️  API: https://shadowcore.club/api/threat/"
    echo "💚 Health: https://shadowcore.club/health"
else
    echo "⚠️  HTTPS still not responding"
    echo "Checking port 443..."
    sudo netstat -tlnp | grep :443 || echo "Port 443 not listening"
    echo "Trying HTTP redirect..."
    curl -I http://shadowcore.club/health
fi
