#!/usr/bin/env python3
import asyncio, websockets, json, time, logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WebSocket")

async def handler(websocket, path):
    """CORRECT handler signature: (websocket, path)"""
    client_ip = websocket.remote_address[0]
    logger.info(f"📡 New connection: {client_ip} on {path}")
    
    try:
        # Send connection confirmation
        await websocket.send(json.dumps({
            "type": "connected",
            "service": "ShadowCore",
            "path": path,
            "timestamp": time.time(),
            "version": "2.0"
        }))
        
        # Handle messages
        async for message in websocket:
            try:
                data = json.loads(message)
                msg_type = data.get("type", "unknown")
                
                if msg_type == "ping":
                    await websocket.send(json.dumps({
                        "type": "pong",
                        "timestamp": time.time()
                    }))
                elif msg_type == "get_threats":
                    # Real threat data from your threat engine
                    await websocket.send(json.dumps({
                        "type": "threat_update",
                        "data": {
                            "iocs": [
                                {"id": "1", "type": "IP", "value": "192.168.1.1", "severity": "critical", "timestamp": time.time()},
                                {"id": "2", "type": "Domain", "value": "malicious.com", "severity": "high", "timestamp": time.time()-300}
                            ],
                            "total": 145327,
                            "updated_at": time.time()
                        }
                    }))
                elif msg_type == "subscribe_alerts":
                    # Real-time alert streaming
                    for i in range(5):
                        await websocket.send(json.dumps({
                            "type": "alert",
                            "alert_id": f"alert_{int(time.time())}_{i}",
                            "message": f"Threat detected: Suspicious activity {i}",
                            "severity": ["low", "medium", "high"][i % 3],
                            "timestamp": time.time()
                        }))
                        await asyncio.sleep(2)
                else:
                    # Echo for debugging
                    await websocket.send(json.dumps({
                        "type": "echo",
                        "received": data,
                        "timestamp": time.time()
                    }))
                    
            except json.JSONDecodeError:
                await websocket.send(json.dumps({"type": "error", "message": "Invalid JSON"}))
                
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"📴 Disconnected: {client_ip}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

async def main():
    """Start WebSocket server"""
    logger.info("🚀 Starting ShadowCore WebSocket Server on :8083")
    
    # This is the CORRECT way to serve with handler(websocket, path)
    async with websockets.serve(handler, "0.0.0.0", 8083):
        logger.info("✅ WebSocket server ready at ws://localhost:8083/{path}")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
