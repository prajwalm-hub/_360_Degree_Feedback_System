"""
WebSocket server for real-time news broadcasting.
Provides live updates to frontend clients.
"""

import asyncio
import json
import logging
from typing import Dict, Set, Any
import websockets
from websockets.exceptions import ConnectionClosedError

from config.realtime_config import realtime_config
from queue_manager import websocket_broadcaster

logger = logging.getLogger(__name__)

class NewsWebSocketServer:
    """WebSocket server for real-time news updates"""

    def __init__(self):
        self.connected_clients: Set[websockets.WebSocketServerProtocol] = set()
        self.server = None
        self.running = False

    async def start(self):
        """Start the WebSocket server"""
        try:
            self.running = True
            self.server = await websockets.serve(
                self._handle_client,
                realtime_config.websocket_host,
                realtime_config.websocket_port,
                ping_interval=realtime_config.websocket_ping_interval
            )

            logger.info(f"WebSocket server started on ws://{realtime_config.websocket_host}:{realtime_config.websocket_port}")

            # Keep the server running
            await self.server.wait_closed()

        except Exception as e:
            logger.error(f"Failed to start WebSocket server: {e}")
            raise

    def stop(self):
        """Stop the WebSocket server"""
        self.running = False
        if self.server:
            self.server.close()
        logger.info("WebSocket server stopped")

    async def _handle_client(self, websocket, path=None):
        """Handle individual WebSocket client connections"""
        # Add client to broadcaster
        websocket_broadcaster.add_client(websocket)

        try:
            logger.info(f"New WebSocket client connected from {websocket.remote_address}")

            # Send welcome message
            welcome_message = {
                'type': 'welcome',
                'message': 'Connected to NewsScope India real-time feed',
                'timestamp': asyncio.get_event_loop().time()
            }
            await websocket.send(json.dumps(welcome_message))

            # Keep connection alive and handle client messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self._handle_client_message(websocket, data)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON received from client: {message}")
                except Exception as e:
                    logger.error(f"Error handling client message: {e}")

        except ConnectionClosedError:
            logger.info(f"WebSocket client disconnected: {websocket.remote_address}")
        except Exception as e:
            logger.error(f"WebSocket client error: {e}")
        finally:
            # Remove client from broadcaster
            websocket_broadcaster.remove_client(websocket)

    async def _handle_client_message(self, websocket, data: Dict[str, Any]):
        """Handle messages from WebSocket clients"""
        message_type = data.get('type', '')

        if message_type == 'subscribe':
            # Client wants to subscribe to specific topics
            topics = data.get('topics', [])
            logger.info(f"Client subscribed to topics: {topics}")

            # Send acknowledgment
            ack_message = {
                'type': 'subscribed',
                'topics': topics,
                'timestamp': asyncio.get_event_loop().time()
            }
            await websocket.send(json.dumps(ack_message))

        elif message_type == 'ping':
            # Respond to ping
            pong_message = {
                'type': 'pong',
                'timestamp': asyncio.get_event_loop().time()
            }
            await websocket.send(json.dumps(pong_message))

        elif message_type == 'get_stats':
            # Send current statistics
            stats = await self._get_server_stats()
            stats_message = {
                'type': 'stats',
                'data': stats,
                'timestamp': asyncio.get_event_loop().time()
            }
            await websocket.send(json.dumps(stats_message))

        else:
            logger.warning(f"Unknown message type: {message_type}")

    async def _get_server_stats(self) -> Dict[str, Any]:
        """Get server statistics"""
        return {
            'connected_clients': len(websocket_broadcaster.connected_clients),
            'uptime': asyncio.get_event_loop().time(),  # Simplified uptime
            'server_version': '1.0.0'
        }

    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        await websocket_broadcaster.broadcast_article(message)

class NewsWebSocketClient:
    """WebSocket client for testing (can be used by frontend)"""

    def __init__(self, uri: str):
        self.uri = uri
        self.websocket = None

    async def connect(self):
        """Connect to WebSocket server"""
        try:
            self.websocket = await websockets.connect(self.uri)
            logger.info(f"Connected to WebSocket server: {self.uri}")
        except Exception as e:
            logger.error(f"Failed to connect to WebSocket server: {e}")
            raise

    async def disconnect(self):
        """Disconnect from WebSocket server"""
        if self.websocket:
            await self.websocket.close()
            logger.info("Disconnected from WebSocket server")

    async def send_message(self, message: Dict[str, Any]):
        """Send message to server"""
        if self.websocket:
            await self.websocket.send(json.dumps(message))

    async def receive_messages(self):
        """Receive messages from server"""
        if not self.websocket:
            return

        try:
            async for message in self.websocket:
                data = json.loads(message)
                logger.info(f"Received: {data}")
                yield data
        except Exception as e:
            logger.error(f"Error receiving messages: {e}")

# Global server instance
websocket_server = NewsWebSocketServer()

async def start_websocket_server():
    """Start the WebSocket server"""
    await websocket_server.start()

async def stop_websocket_server():
    """Stop the WebSocket server"""
    websocket_server.stop()

async def broadcast_news_article(article: Dict[str, Any]):
    """Broadcast a news article to all connected clients"""
    await websocket_server.broadcast_to_all(article)

if __name__ == "__main__":
    # Test the WebSocket server
    async def test_server():
        # Start server in background
        server_task = asyncio.create_task(start_websocket_server())

        # Wait a bit
        await asyncio.sleep(1)

        # Test client
        client = NewsWebSocketClient(f"ws://{realtime_config.websocket_host}:{realtime_config.websocket_port}")

        try:
            await client.connect()

            # Subscribe to news
            await client.send_message({
                'type': 'subscribe',
                'topics': ['government', 'politics']
            })

            # Listen for messages
            async for message in client.receive_messages():
                print(f"Received: {message}")
                break  # Just receive one message for testing

        except Exception as e:
            print(f"Test failed: {e}")
        finally:
            await client.disconnect()
            websocket_server.stop()

    asyncio.run(test_server())
