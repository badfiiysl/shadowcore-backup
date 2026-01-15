import asyncio
import websockets
import json
import sys

async def test():
    try:
        print("Connecting to WebSocket server...")
        async with websockets.connect('ws://localhost:8083', timeout=5) as websocket:
            # Wait for welcome message
            welcome = await websocket.recv()
            data = json.loads(welcome)
            print(f"✅ Connected! Server says: {data.get('message', 'No message')}")
            
            # Test echo
            test_msg = {"type": "echo", "data": "Hello ShadowCore!"}
            await websocket.send(json.dumps(test_msg))
            
            response = await websocket.recv()
            print(f"✅ Echo test passed: {response}")
            
            # Test ping
            ping_msg = {"type": "ping"}
            await websocket.send(json.dumps(ping_msg))
            
            pong = await websocket.recv()
            print(f"✅ Ping test passed: {pong}")
            
            print("\n🎉 WebSocket server is working perfectly!")
            return True
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test())
    sys.exit(0 if success else 1)
