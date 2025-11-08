import asyncio
import json
import websockets
from websockets.exceptions import ConnectionClosedError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_subscription():
    """Test client subscription functionality"""
    uri = "ws://localhost:8765"
    try:
        async with websockets.connect(uri) as websocket:
            # Receive welcome message
            welcome = await websocket.recv()
            welcome_data = json.loads(welcome)
            logger.info(f"Received welcome: {welcome_data}")

            # Send subscribe message
            subscribe_msg = {
                'type': 'subscribe',
                'topics': ['government', 'politics']
            }
            await websocket.send(json.dumps(subscribe_msg))

            # Receive acknowledgment
            ack = await websocket.recv()
            ack_data = json.loads(ack)
            logger.info(f"Received acknowledgment: {ack_data}")

            assert ack_data['type'] == 'subscribed'
            assert ack_data['topics'] == ['government', 'politics']
            logger.info("Subscription test passed")

    except Exception as e:
        logger.error(f"Subscription test failed: {e}")
        raise

async def test_ping_pong():
    """Test ping/pong functionality"""
    uri = "ws://localhost:8765"
    try:
        async with websockets.connect(uri) as websocket:
            # Receive welcome
            await websocket.recv()

            # Send ping
            ping_msg = {'type': 'ping'}
            await websocket.send(json.dumps(ping_msg))

            # Receive pong
            pong = await websocket.recv()
            pong_data = json.loads(pong)
            logger.info(f"Received pong: {pong_data}")

            assert pong_data['type'] == 'pong'
            logger.info("Ping/pong test passed")

    except Exception as e:
        logger.error(f"Ping/pong test failed: {e}")
        raise

async def test_get_stats():
    """Test getting server stats"""
    uri = "ws://localhost:8765"
    try:
        async with websockets.connect(uri) as websocket:
            # Receive welcome
            await websocket.recv()

            # Send get_stats
            stats_msg = {'type': 'get_stats'}
            await websocket.send(json.dumps(stats_msg))

            # Receive stats
            stats = await websocket.recv()
            stats_data = json.loads(stats)
            logger.info(f"Received stats: {stats_data}")

            assert stats_data['type'] == 'stats'
            assert 'connected_clients' in stats_data['data']
            logger.info("Get stats test passed")

    except Exception as e:
        logger.error(f"Get stats test failed: {e}")
        raise

async def test_invalid_json():
    """Test handling of invalid JSON"""
    uri = "ws://localhost:8765"
    try:
        async with websockets.connect(uri) as websocket:
            # Receive welcome
            await websocket.recv()

            # Send invalid JSON
            await websocket.send("invalid json")

            # Should not crash, connection should remain or close gracefully
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                logger.warning(f"Unexpected response to invalid JSON: {response}")
            except asyncio.TimeoutError:
                logger.info("No response to invalid JSON, as expected")

            logger.info("Invalid JSON test passed")

    except Exception as e:
        logger.error(f"Invalid JSON test failed: {e}")
        raise

async def test_multiple_clients():
    """Test multiple concurrent clients"""
    uri = "ws://localhost:8765"
    clients = []

    async def client_task(client_id):
        try:
            async with websockets.connect(uri) as websocket:
                # Receive welcome
                welcome = await websocket.recv()
                welcome_data = json.loads(welcome)
                logger.info(f"Client {client_id} received welcome")

                # Subscribe
                subscribe_msg = {'type': 'subscribe', 'topics': ['test']}
                await websocket.send(json.dumps(subscribe_msg))

                # Receive ack
                ack = await websocket.recv()
                ack_data = json.loads(ack)
                logger.info(f"Client {client_id} received ack")

                # Wait a bit
                await asyncio.sleep(0.5)

        except Exception as e:
            logger.error(f"Client {client_id} failed: {e}")
            raise

    # Create multiple clients
    tasks = [client_task(i) for i in range(5)]
    await asyncio.gather(*tasks)
    logger.info("Multiple clients test passed")

async def run_tests():
    """Run all tests"""
    logger.info("Starting WebSocket server tests...")

    try:
        await test_subscription()
        await test_ping_pong()
        await test_get_stats()
        await test_invalid_json()
        await test_multiple_clients()

        logger.info("All tests passed!")

    except Exception as e:
        logger.error(f"Tests failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_tests())
