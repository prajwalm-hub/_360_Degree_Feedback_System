"""
Main orchestrator for the real-time news monitoring system.
Coordinates collectors, processors, and broadcasters.
"""

import asyncio
import logging
import signal
import sys
import os
from typing import List, Dict, Any

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from realtime_collector import RealTimeCollector
from queue_manager import queue_manager, initialize_queue_system, shutdown_queue_system
from websocket_server import start_websocket_server, stop_websocket_server
from advanced_nlp import nlp_processor

# Try to import Redis, fallback to mock if not available
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Redis not available, using in-memory storage")

from config.realtime_config import realtime_config

logger = logging.getLogger(__name__)

class MockRedis:
    """Mock Redis implementation for testing without Redis"""

    def __init__(self):
        self.data = {}

    async def ping(self):
        return True

    async def set(self, key, value):
        self.data[key] = value

    async def get(self, key):
        return self.data.get(key)

    async def delete(self, key):
        if key in self.data:
            del self.data[key]

    async def close(self):
        pass

class RealTimeNewsSystem:
    """Main real-time news monitoring system"""

    def __init__(self):
        self.collector = None
        self.redis_client = None
        self.running = False
        self.tasks: List[asyncio.Task] = []

    async def initialize(self):
        """Initialize all system components"""
        try:
            logger.info("Initializing real-time news monitoring system...")

            # Initialize Redis or mock Redis
            if REDIS_AVAILABLE and realtime_config.redis_enabled:
                self.redis_client = redis.Redis(
                    host=realtime_config.redis_host,
                    port=realtime_config.redis_port,
                    db=realtime_config.redis_db,
                    decode_responses=True
                )
                # Test Redis connection
                await self.redis_client.ping()
                logger.info("Redis connection established")
            else:
                # Use mock Redis for testing
                self.redis_client = MockRedis()
                logger.info("Using mock Redis (in-memory storage)")

            # Initialize queue system
            await initialize_queue_system()

            # Initialize collector
            self.collector = RealTimeCollector(self.redis_client)

            # Get model info
            model_info = await nlp_processor.get_model_info()
            logger.info(f"AI Models loaded: {model_info}")

            logger.info("System initialization complete")

        except Exception as e:
            logger.error(f"Failed to initialize system: {e}")
            raise

    async def start(self):
        """Start the real-time news monitoring system"""
        try:
            self.running = True
            logger.info("Starting real-time news monitoring system...")

            # Start WebSocket server
            websocket_task = asyncio.create_task(start_websocket_server())
            self.tasks.append(websocket_task)

            # Start queue processing
            processing_task = asyncio.create_task(
                queue_manager.start_processing(realtime_config.processing_workers)
            )
            self.tasks.append(processing_task)

            # Start news collection
            async with self.collector:
                collection_task = asyncio.create_task(self.collector.start_collection())
                self.tasks.append(collection_task)

                # Wait for all tasks
                await asyncio.gather(*self.tasks, return_exceptions=True)

        except Exception as e:
            logger.error(f"Error starting system: {e}")
            await self.stop()
            raise

    async def stop(self):
        """Stop the real-time news monitoring system"""
        logger.info("Stopping real-time news monitoring system...")

        self.running = False

        # Stop collector
        if self.collector:
            self.collector.stop_collection()

        # Stop queue processing
        queue_manager.stop_processing()

        # Stop WebSocket server
        stop_websocket_server()

        # Cancel all tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()

        # Shutdown queue system
        await shutdown_queue_system()

        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()

        logger.info("System stopped")

    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status and statistics"""
        try:
            # Get queue stats
            queue_stats = await queue_manager.get_queue_stats()

            # Get model info
            model_info = await nlp_processor.get_model_info()

            return {
                'running': self.running,
                'queue_stats': queue_stats,
                'model_info': model_info,
                'config': {
                    'workers': realtime_config.processing_workers,
                    'batch_size': realtime_config.ai_batch_size,
                    'websocket_port': realtime_config.websocket_port,
                    'redis_host': realtime_config.redis_host
                }
            }

        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {'error': str(e)}

# Global system instance
news_system = RealTimeNewsSystem()

async def main():
    """Main entry point"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Setup signal handlers
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(news_system.stop())

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Initialize and start system
        await news_system.initialize()
        await news_system.start()

    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.error(f"System error: {e}")
        sys.exit(1)
    finally:
        await news_system.stop()

if __name__ == "__main__":
    asyncio.run(main())
