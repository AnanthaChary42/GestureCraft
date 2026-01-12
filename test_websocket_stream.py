import asyncio
import websockets
import json

async def receive_data():
    uri = "ws://localhost:8765"
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected! Listening for gestures...")
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                
                # Pretty print nicely aligned
                gesture = data.get("gesture", "NONE")
                presence = "HAND" if data.get("hand_detected") else "NO HAND"
                print(f"STATUS: [{presence}] GESTURE: [{gesture}]")
                
    except ConnectionRefusedError:
        print("Connection failed. Is main.py running?")
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed by server.")

if __name__ == "__main__":
    asyncio.run(receive_data())
