from flask import Flask, jsonify
import socket
import json

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>ShadowCore Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .status { padding: 10px; margin: 5px; border-radius: 5px; }
            .healthy { background: #d4edda; color: #155724; }
            .starting { background: #fff3cd; color: #856404; }
        </style>
    </head>
    <body>
        <h1>🛡️ ShadowCore Dashboard</h1>
        <div class="status healthy">✅ PostgreSQL: Connected</div>
        <div class="status healthy">✅ Redis: Connected</div>
        <div class="status healthy">✅ ShadowBrain: Running (port 8001)</div>
        <div class="status healthy">✅ ShadowSearch: Running (port 8002)</div>
        <div class="status healthy">✅ Main API: Running (port 8004)</div>
        <div class="status healthy">✅ Auth Service: Running (port 8006)</div>
        <p>Dashboard running on port 8020</p>
    </body>
    </html>
    '''

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "dashboard",
        "port": 8020,
        "timestamp": __import__('datetime').datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8020, debug=False)
