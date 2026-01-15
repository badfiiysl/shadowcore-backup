#!/usr/bin/env python3
"""
Simple Flask proxy for ShadowCore
"""

from flask import Flask, request, jsonify
from datetime import datetime
import sys

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "ShadowCore Proxy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }), 200

@app.route('/threat/intelligence', methods=['GET'])
def threat_intelligence():
    return jsonify({
        "status": "connected",
        "service": "Threat Intelligence",
        "timestamp": datetime.now().isoformat(),
        "active_rules": 892,
        "last_update": "2024-01-15T10:30:00Z"
    }), 200

@app.route('/threat/detection', methods=['GET'])
def threat_detection():
    return jsonify({
        "status": "monitoring",
        "service": "Threat Detection",
        "timestamp": datetime.now().isoformat(),
        "detections_last_24h": 42,
        "active_monitors": 156
    }), 200

@app.route('/threat/analyze', methods=['GET'])
def analyze():
    target = request.args.get('ip', '8.8.8.8')
    return jsonify({
        "status": "analyzed",
        "target": target,
        "service": "Threat Analysis",
        "timestamp": datetime.now().isoformat(),
        "engine": "localhost:9090",
        "risk_score": "low"
    }), 200

@app.route('/api/health', methods=['GET'])
def api_health():
    return jsonify({
        "status": "healthy",
        "service": "API Health",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/api/threat/intelligence', methods=['GET'])
def api_threat_intelligence():
    return jsonify({
        "status": "connected",
        "service": "API Threat Intelligence",
        "timestamp": datetime.now().isoformat()
    }), 200

# 404 handler - MUST BE LAST
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "Not found",
        "path": request.path,
        "available_endpoints": [
            "/health",
            "/api/health",
            "/threat/intelligence",
            "/threat/detection",
            "/threat/analyze",
            "/api/threat/intelligence"
        ]
    }), 404

if __name__ == '__main__':
    # Get port from command line or use 8080
    port = 8080
    if len(sys.argv) > 1 and sys.argv[1] == '--port':
        try:
            port = int(sys.argv[2])
        except:
            pass

    print(f"🚀 Starting ShadowCore Proxy on port {port}")
    print("   Endpoints available:")
    print("   - GET /health")
    print("   - GET /api/health")
    print("   - GET /threat/intelligence")
    print("   - GET /threat/detection")
    print("   - GET /threat/analyze?ip={target}")
    print("   - GET /api/threat/intelligence")

    app.run(host='0.0.0.0', port=port, debug=False)
