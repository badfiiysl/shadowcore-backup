#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class ThreatAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {"status": "healthy", "service": "Threat API", "port": 8003}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {
                "service": "ShadowCore Threat API",
                "version": "1.0.0",
                "port": 8003,
                "endpoints": ["/health", "/threat/analyze"]
            }
            self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = {"status": "received", "method": "POST", "path": self.path}
        self.wfile.write(json.dumps(response).encode())

if __name__ == '__main__':
    import sys
    port = 8003
    if len(sys.argv) > 2 and sys.argv[1] == '--port':
        port = int(sys.argv[2])
    
    server = HTTPServer(('0.0.0.0', port), ThreatAPIHandler)
    print(f"Threat API running on port {port}")
    server.serve_forever()
