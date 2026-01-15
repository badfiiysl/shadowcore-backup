#!/usr/bin/env python3
"""
Simple Threat API for ShadowCore - FIXED
Provides REST API for threat analysis
"""
from flask import Flask, request, jsonify
import json
import sys
import os

sys.path.insert(0, '/opt/shadowcore')
from clean_orchestrator_fixed import CleanShadowCoreOrchestrator
import asyncio

app = Flask(__name__)

# Global orchestrator instance
orchestrator = None

def init_orchestrator():
    """Initialize the orchestrator"""
    global orchestrator
    if orchestrator is None:
        print("🔧 Initializing orchestrator for API...")
        orchestrator = CleanShadowCoreOrchestrator()
        print("✅ Orchestrator ready for API requests")

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'ShadowCore Threat API',
        'version': '2.0.0',
        'threat_cache': '49,088 threats',
        'endpoints': {
            '/health': 'Health check',
            '/analyze?ioc=<value>': 'Analyze single IOC',
            '/bulk_analyze': 'Analyze multiple IOCs (POST JSON)'
        }
    })

@app.route('/analyze', methods=['GET'])
def analyze():
    """Analyze an IOC"""
    ioc = request.args.get('ioc', '')
    if not ioc:
        return jsonify({'error': 'No IOC provided'}), 400

    print(f"🔍 API Request: Analyzing {ioc}")

    try:
        # Initialize if needed
        if orchestrator is None:
            init_orchestrator()

        # Run async analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(orchestrator.process_ioc(ioc))
        loop.close()

        # Format response
        response = {
            'ioc': ioc,
            'threat_level': result['threat_assessment']['level'],
            'confidence': result['threat_assessment']['confidence'],
            'malware': result.get('malware', 'unknown'),
            'source': result.get('source', 'unknown'),
            'analysis_time': result['metadata']['analysis_time'],
            'report_id': result['metadata']['report_id']
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e), 'ioc': ioc}), 500

@app.route('/bulk_analyze', methods=['POST'])
def bulk_analyze():
    """Analyze multiple IOCs"""
    try:
        data = request.get_json()
        iocs = data.get('iocs', [])

        if not iocs:
            return jsonify({'error': 'No IOCs provided'}), 400

        # Initialize if needed
        if orchestrator is None:
            init_orchestrator()

        results = []
        for ioc in iocs[:10]:  # Limit to 10 for performance
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(orchestrator.process_ioc(ioc))
                loop.close()

                results.append({
                    'ioc': ioc,
                    'threat_level': result['threat_assessment']['level'],
                    'confidence': result['threat_assessment']['confidence']
                })
            except:
                results.append({
                    'ioc': ioc,
                    'error': 'Analysis failed'
                })

        return jsonify({
            'count': len(results),
            'results': results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting ShadowCore Threat API (FIXED)...")
    print("📡 Endpoints:")
    print("  GET /health - Health check")
    print("  GET /analyze?ioc=<value> - Analyze single IOC")
    print("  POST /bulk_analyze - Analyze multiple IOCs (JSON)")
    print("\n🔧 Initializing orchestrator...")
    init_orchestrator()
    print("✅ Ready on port 8003")
    app.run(host='0.0.0.0', port=8003, debug=False, threaded=True)
