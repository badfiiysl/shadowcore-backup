#!/bin/bash
echo "🔒 HTTPS DIAGNOSTIC TEST"
echo "========================"
date
echo ""

# 1. Check Nginx
echo "1️⃣  NGINX STATUS:"
sudo systemctl is-active nginx && echo "✅ Active" || echo "❌ Inactive"

# 2. Check ports
echo "2️⃣  PORTS LISTENING:"
echo "Port 80:"
sudo ss -tulpn | grep ":80 " || echo "  ❌ Not listening"
echo "Port 443:"
sudo ss -tulpn | grep ":443 " || echo "  ❌ Not listening"

# 3. Check config
echo "3️⃣  NGINX CONFIG (listen lines):"
sudo grep -n "listen" /etc/nginx/sites-available/shadowcore || echo "  No listen directives found!"

# 4. Check certs
echo "4️⃣  SSL CERTIFICATES:"
sudo ls -la /etc/letsencrypt/live/shadowcore.club-0001/ 2>/dev/null || echo "  ❌ Certificate directory missing"

# 5. Test connections
echo "5️⃣  CONNECTION TESTS:"
echo "  HTTP (should redirect):"
curl -I http://shadowcore.club 2>/dev/null | head -1 || echo "    ❌ HTTP failed"
echo "  HTTPS (should work):"
curl -I https://shadowcore.club 2>/dev/null | head -1 || echo "    ❌ HTTPS failed"

# 6. Direct backend test
echo "6️⃣  BACKEND SERVICES:"
curl -s http://localhost:3002 >/dev/null 2>&1 && echo "  ✅ React UI (3002)" || echo "  ❌ React UI down"
curl -s "http://localhost:8003/health" >/dev/null 2>&1 && echo "  ✅ Threat API (8003)" || echo "  ❌ Threat API down"
