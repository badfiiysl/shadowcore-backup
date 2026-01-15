#!/usr/bin/env python3
"""
THREATINSIGHT API SERVER
REST API for threat intelligence queries
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Import ThreatInsight
try:
    from threat_insight import ThreatInsight
    insight = ThreatInsight()
    CORE_AVAILABLE = True
    print("✅ ThreatInsight core loaded successfully")
except ImportError as e:
    print(f"⚠️  Failed to load ThreatInsight core: {e}")
    CORE_AVAILABLE = False

@app.route('/')
def index():
    """API documentation"""
    return jsonify({
        'service': 'ThreatInsight API',
        'version': '2.0.0',
        'endpoints': {
            '/api/health': 'GET - Service health check',
            '/api/analyze/ip/<ip>': 'GET - Analyze IP address',
            '/api/analyze/domain/<domain>': 'GET - Analyze domain',
            '/api/batch': 'POST - Batch analysis',
            '/api/stats': 'GET - System statistics'
        },
        'status': 'online' if CORE_AVAILABLE else 'core_unavailable'
    })

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'ThreatInsight API',
        'version': '2.0.0',
        'core_available': CORE_AVAILABLE,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/analyze/ip/<ip_address>')
def analyze_ip(ip_address):
    """Analyze IP address"""
    if not CORE_AVAILABLE:
        return jsonify({'error': 'ThreatInsight core not available'}), 500
    
    try:
        # Get analysis mode from query parameter
        mode = request.args.get('mode', 'full')
        full_analysis = (mode.lower() == 'full')
        
        result = insight.analyze_ip(ip_address, full_analysis)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze/domain/<domain>')
def analyze_domain(domain):
    """Analyze domain"""
    if not CORE_AVAILABLE:
        return jsonify({'error': 'ThreatInsight core not available'}), 500
    
    try:
        result = insight.analyze_domain(domain)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch', methods=['POST'])
def batch_analysis():
    """Batch analysis of multiple entities"""
    if not CORE_AVAILABLE:
        return jsonify({'error': 'ThreatInsight core not available'}), 500
    
    try:
        data = request.json
        entities = data.get('entities', [])
        results = []
        
        for entity in entities[:10]:  # Limit to 10 per batch
            if entity.get('type') == 'ip':
                result = insight.analyze_ip(entity.get('value'), full_analysis=False)
                results.append({
                    'entity': entity.get('value'),
                    'type': 'ip',
                    'threat_score': result.get('risk_assessment', {}).get('threat_score', 0),
                    'risk_level': result.get('risk_assessment', {}).get('risk_level', 'unknown'),
                    'country': result.get('geolocation', {}).get('country', 'Unknown'),
                    'isp': result.get('network', {}).get('isp', 'Unknown')
                })
        
        return jsonify({'results': results, 'count': len(results)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Get system statistics"""
    if not CORE_AVAILABLE:
        return jsonify({'error': 'ThreatInsight core not available'}), 500
    
    return jsonify({
        'threat_database': {
            'malicious_ips': len(insight.threat_data['malicious_ips']),
            'malicious_domains': len(insight.threat_data['malicious_domains']),
            'vpn_providers': len(insight.threat_data['vpn_providers']['asns']),
            'high_risk_countries': len(insight.threat_data['high_risk_countries'])
        },
        'system': {
            'version': insight.version,
            'name': insight.name,
            'cache_size': len(insight.cache) if hasattr(insight, 'cache') else 0
        }
    })

if __name__ == '__main__':
    from datetime import datetime
    print("🌐 Starting ThreatInsight API Server...")
    print("📊 API Documentation: http://localhost:9090")
    print("🔧 Health Check: http://localhost:9090/api/health")
    print("🔍 Example: http://localhost:9090/api/analyze/ip/185.130.5.253")
    app.run(host='0.0.0.0', port=9090, debug=False)
