#!/usr/bin/env python3
import ssl, socket, hashlib, json, sys
from datetime import datetime

def check_endpoint(host, port=443):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cipher = ssock.cipher()
                cert = ssock.getpeercert()
                return {
                    "host": host,
                    "port": port,
                    "cipher": cipher[0] if cipher else "unknown",
                    "protocol": ssock.version(),
                    "cert_algorithm": cert.get("signatureAlgorithm", "unknown") if cert else "unknown",
                    "status": "success"
                }
    except Exception as e:
        return {"host": host, "port": port, "status": "error", "error": str(e)}

# Test local services
results = []
for port in [443, 8001, 8004, 8006]:
    results.append(check_endpoint("localhost", port))

print(json.dumps({
    "timestamp": datetime.now().isoformat(),
    "crypto_inventory": results,
    "quantum_status": "inventory_possible"
}))
