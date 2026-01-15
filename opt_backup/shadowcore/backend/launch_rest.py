#!/usr/bin/env python3
"""
ShadowCore REST API Launcher
Start with: python launch_rest.py
"""
import uvicorn
import sys
import os
import argparse
from pathlib import Path

# Parse command line arguments
parser = argparse.ArgumentParser(description='ShadowCore REST API Server')
parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
parser.add_argument('--reload', action='store_true', help='Enable auto-reload for development')
parser.add_argument('--workers', type=int, default=1, help='Number of worker processes')
parser.add_argument('--log-level', default='info', choices=['debug', 'info', 'warning', 'error', 'critical'])
args = parser.parse_args()

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    print(f"""
    🚀 Starting ShadowCore REST API
    ├── Host: {args.host}
    ├── Port: {args.port}
    ├── Workers: {args.workers}
    ├── Reload: {args.reload}
    ├── Log Level: {args.log_level}
    └── API Docs: http://{args.host}:{args.port}/docs
    """)
    
    uvicorn.run(
        "rest.api:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,
        access_log=True,
        workers=args.workers if not args.reload else 1
    )
