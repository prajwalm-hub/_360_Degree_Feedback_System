import sys
sys.path.append('.')

from config.realtime_config import realtime_config

print(f"WebSocket Host: {realtime_config.websocket_host}")
print(f"WebSocket Port: {realtime_config.websocket_port}")
print(f"Full URI: ws://{realtime_config.websocket_host}:{realtime_config.websocket_port}")
