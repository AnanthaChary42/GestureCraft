import asyncio
import websockets
import json
import threading
import time

class SocketServer:
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.connected_clients = set()
        self.loop = None # Will be set in the thread
        
        # Start the server logic in a separate thread
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()
        print(f"[SocketServer] WebSocket Server starting at ws://{host}:{port}...")

    def _run_server(self):
        # Use asyncio.run() to manage the event loop properly in this thread
        try:
            asyncio.run(self._driver())
        except Exception as e:
            print(f"[SocketServer] Server thread error: {e}")

    async def _driver(self):
        # Capture the loop so send_data can use it
        self.loop = asyncio.get_running_loop()
        
        # Start the server using the context manager pattern
        print(f"[SocketServer] Starting on ws://{self.host}:{self.port}")
        async with websockets.serve(self._handler, self.host, self.port):
            await asyncio.Future() # Run forever

    async def _handler(self, websocket):  # Accept all
        # Register client
        self.connected_clients.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            self.connected_clients.remove(websocket)

    def send_data(self, data):
        """
        Thread-safe method to broadcast data to all connected clients.
        """
        # If loop isn't ready or closed, don't try to send
        if not self.connected_clients or self.loop is None or self.loop.is_closed():
            return

        json_data = json.dumps(data)
        
        async def broadcast():
            dead_sockets = set()
            for ws in self.connected_clients:
                try:
                    await ws.send(json_data)
                except Exception:
                    dead_sockets.add(ws)
            
            # Cleanup dead sockets
            for ws in dead_sockets:
                self.connected_clients.discard(ws)

        try:
            asyncio.run_coroutine_threadsafe(broadcast(), self.loop)
        except RuntimeError:
            pass # Loop might be closing
