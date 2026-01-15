#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys

class MainAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if self.path == '/health':
            response = {"status": "healthy", "service": "Main API", "port": 8004}
        elif self.path == '/api/services':
            response = {
                "services": [
                    {"name": "ShadowBrain", "port": 8001, "status": "active"},
                    {"name": "ShadowSearch", "port": 8002, "status": "active"},
                    {"name": "Threat API", "port": 8003, "status": "active"},
                    {"name": "Main API", "port": 8004, "status": "active"},
                    {"name": "Web UI", "port": 8005, "status": "active"},
                    {"name": "Auth Service", "port": 8006, "status": "active"}
                ]
            }
        else:
            response = {
                "service": "ShadowCore Main API",
                "version": "1.0.0",
                "port": 8004,
                "endpoints": ["/health", "/api/services", "/api/status"]
            }
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == '__main__':
    port = 8004
    if len(sys.argv) > 2 and sys.argv[1] == '--port':
        port = int(sys.argv[2])
    
    server = HTTPServer(('0.0.0.0', port), MainAPIHandler)
    print(f"Main API running on port {port}")
    server.serve_forever()
