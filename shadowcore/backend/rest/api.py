"""
ShadowCore REST API Module
This is what launch_rest.py expects to find at 'rest.api:app'
"""
from fastapi import FastAPI, HTTPException
from typing import Dict, Any, List
import datetime

app = FastAPI(
    title="ShadowCore REST API",
    description="Core REST API service for ShadowCore Security Platform",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Health endpoint
@app.get("/health")
async def health() -> Dict[str, str]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "shadowcore-rest-api",
        "timestamp": datetime.datetime.now().isoformat()
    }

# Root endpoint
@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint with service information"""
    return {
        "service": "ShadowCore REST API",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "services": "/api/services",
            "status": "/api/status"
        },
        "timestamp": datetime.datetime.now().isoformat()
    }

# Services endpoint
@app.get("/api/services")
async def get_services() -> Dict[str, List[Dict]]:
    """Get all registered services"""
    return {
        "services": [
            {"name": "Main REST API", "port": 8000, "status": "running", "type": "fastapi"},
            {"name": "Threat API", "port": 8003, "status": "running", "type": "flask"},
            {"name": "Main API", "port": 8004, "status": "running", "type": "flask"},
            {"name": "Auth API", "port": 8006, "status": "running", "type": "fastapi"},
            {"name": "Proxy", "port": 8080, "status": "running", "type": "flask"},
            {"name": "WebSocket", "port": 8083, "status": "running", "type": "websocket"},
            {"name": "UI Dashboard", "port": 8020, "status": "running", "type": "flask"},
            {"name": "Threat Insight", "port": 9090, "status": "running", "type": "flask"}
        ]
    }

# Status endpoint
@app.get("/api/status")
async def get_status() -> Dict[str, Any]:
    """Get comprehensive system status"""
    return {
        "system": "ShadowCore Security Platform",
        "version": "2.0.0",
        "status": "operational",
        "timestamp": datetime.datetime.now().isoformat(),
        "components": {
            "api": {"status": "running", "port": 8000},
            "auth": {"status": "running", "port": 8006},
            "proxy": {"status": "running", "port": 8080},
            "dashboard": {"status": "running", "port": 8020},
            "database": {"postgres": "running", "redis": "running", "neo4j": "running"}
        }
    }

# Add some example endpoints
@app.get("/api/version")
async def get_version() -> Dict[str, str]:
    """Get API version"""
    return {"version": "2.0.0", "name": "ShadowCore"}

@app.post("/api/echo")
async def echo(data: Dict[str, Any]) -> Dict[str, Any]:
    """Echo back received data"""
    return {"received": data, "timestamp": datetime.datetime.now().isoformat()}
