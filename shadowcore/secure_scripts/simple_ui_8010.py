#!/usr/bin/env python3
"""
Simple placeholder UI for port 8010
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import sys

class HtmxUIHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """<!DOCTYPE html>
<html>
<head>
    <title>ShadowCore HTMX UI</title>
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <script src="https://unpkg.com/hyperscript.org@0.9.12"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; max-width: 1200px; }
        .card { border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin: 10px; }
        .status { padding: 10px; margin: 5px; border-radius: 5px; }
        .healthy { background: #d4edda; color: #155724; }
        .warning { background: #fff3cd; color: #856404; }
        .error { background: #f8d7da; color: #721c24; }
        button { margin: 5px; padding: 8px 15px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>🛡️ ShadowCore HTMX UI (Placeholder)</h1>
    <p>This is a placeholder for your SSR/HTMX UI. The real UI should be running on port 8010.</p>
    
    <div class="card">
        <h2>System Status</h2>
        <div class="status healthy">✅ ShadowBrain: Running (port 8001)</div>
        <div class="status healthy">✅ ShadowSearch: Running (port 8002)</div>
        <div class="status healthy">✅ Main API: Running (port 8004)</div>
        <div class="status warning">⚠ HTMX UI: Not running (should be on 8010)</div>
        
        <h3>Test HTMX</h3>
        <button hx-get="/api/health" hx-target="#result">Test Health</button>
        <button hx-get="/api/services" hx-target="#result">List Services</button>
        
        <div id="result" style="margin-top: 20px; padding: 10px; border: 1px solid #ccc;"></div>
    </div>
    
    <div class="card">
        <h2>Next Steps:</h2>
        <ol>
            <li>Find your actual SSR/HTMX UI application</li>
            <li>Start it on port 8010</li>
            <li>Update nginx config if needed</li>
            <li>Test the integration</li>
        </ol>
    </div>
    
    <script>
        // Mock API endpoints
        document.addEventListener('DOMContentLoaded', function() {
            htmx.on('htmx:beforeRequest', function(evt) {
                if (evt.detail.path === '/api/health') {
                    evt.preventDefault();
                    document.getElementById('result').innerHTML = 
                        '<div class="status healthy">All systems operational!</div>';
                }
                if (evt.detail.path === '/api/services') {
                    evt.preventDefault();
                    document.getElementById('result').innerHTML = 
                        '<div class="card">' +
                        '<h4>Running Services:</h4>' +
                        '<ul>' +
                        '<li>ShadowBrain (8001) - AI Processing</li>' +
                        '<li>ShadowSearch (8002) - Search Engine</li>' +
                        '<li>Main API (8004) - Core API</li>' +
                        '<li>Auth Service (8006) - Authentication</li>' +
                        '<li>Threat API (8003) - Threat Intelligence</li>' +
                        '</ul></div>';
                }
            });
        });
    </script>
</body>
</html>"""
            self.wfile.write(html.encode())
        else:
            super().do_GET()

def run(port=8010):
    os.chdir('/tmp')
    server = HTTPServer(('127.0.0.1', port), HtmxUIHandler)
    print(f"Starting placeholder UI on http://127.0.0.1:{port}")
    print("Press Ctrl+C to stop")
    server.serve_forever()

if __name__ == '__main__':
    run()
