import asyncio
import websockets

async def quick_test():
    try:
        async with websockets.connect('ws://localhost:8765') as websocket:
            print("Connected successfully!")
            message = await websocket.recv()
            print(f"Received: {message}")
    except Exception as e:
        print(f"Connection failed: {e}")

asyncio.run(quick_test())
