"""
Redis Streams queue manager for real-time news processing.
Handles queuing, processing, and distribution of news articles.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Callable

# Try to import Redis, fallback to mock if not available
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Redis not available, using in-memory storage")

from config.realtime_config import realtime_config
from advanced_nlp import process_articles_batch

logger = logging.getLogger(__name__)

class MockRedis:
    """Mock Redis implementation for testing without Redis"""

    def __init__(self):
        self.data = {}
        self.streams = {}
        self.groups = {}

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

    async def xadd(self, stream_key, fields, maxlen=None):
        """Mock xadd for streams"""
        if stream_key not in self.streams:
            self.streams[stream_key] = []
        # Simple mock ID generation
        message_id = f"{len(self.streams[stream_key])}-0"
        self.streams[stream_key].append((message_id, fields))
        return message_id

    async def xreadgroup(self, group, consumer, streams, count=None, block=None):
        """Mock xreadgroup"""
        # Simulate blocking behavior
        if block:
            await asyncio.sleep(block / 1000)

        # Return pending messages for the stream
        stream_key = list(streams.keys())[0]
        if stream_key in self.streams:
            # Return all messages (in real Redis, this would be pending messages for the consumer group)
            messages = [(stream_key, self.streams[stream_key])]
            # Clear the stream after reading (simulate consumption)
            self.streams[stream_key] = []
            return messages
        return []

    async def xack(self, stream_key, group, message_id):
        """Mock xack"""
        return 1

    async def xinfo_stream(self, stream_key):
        """Mock xinfo_stream"""
        return {
            'length': len(self.streams.get(stream_key, [])),
            'last-generated-id': f"{len(self.streams.get(stream_key, []))}-0"
        }

    async def xinfo_groups(self, stream_key):
        """Mock xinfo_groups"""
        return []

    async def xinfo_consumers(self, stream_key, group):
        """Mock xinfo_consumers"""
        return []

    async def xgroup_create(self, stream_key, group, start, mkstream=False):
        """Mock xgroup_create"""
        if group not in self.groups:
            self.groups[group] = []
        return True

class QueueManager:
    """Manages Redis Streams for news article processing"""

    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self.consumer_group = "news_processors"
        self.consumer_name = "processor_1"
        self.processing_tasks: List[asyncio.Task] = []
        self.running = False

    async def connect(self):
        """Connect to Redis or use mock Redis"""
        try:
            if REDIS_AVAILABLE and realtime_config.redis_enabled:
                self.redis = redis.Redis(
                    host=realtime_config.redis_host,
                    port=realtime_config.redis_port,
                    db=realtime_config.redis_db,
                    decode_responses=True
                )

                # Test connection
                await self.redis.ping()
                logger.info("Connected to Redis")

                # Create consumer group if it doesn't exist
                try:
                    await self.redis.xgroup_create(
                        realtime_config.redis_stream_key,
                        self.consumer_group,
                        "$",
                        mkstream=True
                    )
                    logger.info(f"Created consumer group: {self.consumer_group}")
                except redis.ResponseError as e:
                    if "BUSYGROUP" not in str(e):
                        raise
            else:
                # Use mock Redis for in-memory storage
                self.redis = MockRedis()
                logger.info("Using mock Redis (in-memory storage)")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
            logger.info("Disconnected from Redis")

    async def start_processing(self, num_workers: int = None):
        """Start processing workers"""
        if num_workers is None:
            num_workers = realtime_config.processing_workers

        self.running = True
        logger.info(f"Starting {num_workers} processing workers")

        # Start worker tasks
        for i in range(num_workers):
            task = asyncio.create_task(self._processing_worker(i))
            self.processing_tasks.append(task)

        # Wait for all tasks
        try:
            await asyncio.gather(*self.processing_tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Processing error: {e}")

    def stop_processing(self):
        """Stop all processing workers"""
        self.running = False
        logger.info("Stopping processing workers")

        # Cancel all tasks
        for task in self.processing_tasks:
            if not task.done():
                task.cancel()

    async def _processing_worker(self, worker_id: int):
        """Individual processing worker"""
        logger.info(f"Worker {worker_id} started")

        while self.running:
            try:
                # Read from stream
                messages = await self.redis.xreadgroup(
                    self.consumer_group,
                    f"processor_{worker_id}",
                    {realtime_config.redis_stream_key: ">"},
                    count=realtime_config.queue_prefetch_count,
                    block=1000  # Block for 1 second
                )

                if not messages:
                    continue

                # Process messages
                for stream_name, message_list in messages:
                    for message_id, message_data in message_list:
                        try:
                            await self._process_message(message_id, message_data)
                        except Exception as e:
                            logger.error(f"Error processing message {message_id}: {e}")

            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(1)

        logger.info(f"Worker {worker_id} stopped")

    async def _process_message(self, message_id: str, message_data: Dict[str, Any]):
        """Process a single message from the queue"""
        try:
            # Parse article data
            article_data = json.loads(message_data['data'])

            # Process through NLP pipeline
            processed_articles = await process_articles_batch([article_data])
            processed_article = processed_articles[0] if processed_articles else article_data

            # Store in database (placeholder - integrate with existing database)
            await self._store_processed_article(processed_article)

            # Broadcast to WebSocket clients
            await self._broadcast_to_clients(processed_article)

            # Acknowledge message
            await self.redis.xack(
                realtime_config.redis_stream_key,
                self.consumer_group,
                message_id
            )

            logger.debug(f"Processed article: {processed_article.get('title', 'Unknown')}")

        except Exception as e:
            logger.error(f"Error processing message {message_id}: {e}")

    async def _store_processed_article(self, article: Dict[str, Any]):
        """Store processed article in database"""
        # Placeholder - integrate with existing database models
        # This would use the existing DatabaseManager and Article model
        logger.debug(f"Storing article: {article.get('title', 'Unknown')}")

        # TODO: Implement database storage
        # db_manager = DatabaseManager()
        # article_obj = Article(**article)
        # db_manager.insert_news_article(article_obj)

    async def _broadcast_to_clients(self, article: Dict[str, Any]):
        """Broadcast processed article to WebSocket clients"""
        # This will be handled by the WebSocket server
        # For now, just log
        logger.debug(f"Broadcasting article: {article.get('title', 'Unknown')}")

    async def enqueue_article(self, article: Dict[str, Any]) -> str:
        """Add article to processing queue"""
        try:
            message_id = await self.redis.xadd(
                realtime_config.redis_stream_key,
                {'data': json.dumps(article)},
                maxlen=realtime_config.redis_max_len
            )
            logger.debug(f"Enqueued article: {article.get('title', 'Unknown')}")
            return message_id
        except Exception as e:
            logger.error(f"Error enqueuing article: {e}")
            raise

    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        try:
            # Get stream info
            stream_info = await self.redis.xinfo_stream(realtime_config.redis_stream_key)

            # Get consumer group info
            try:
                group_info = await self.redis.xinfo_groups(realtime_config.redis_stream_key)
                consumer_info = await self.redis.xinfo_consumers(
                    realtime_config.redis_stream_key,
                    self.consumer_group
                )
            except:
                group_info = []
                consumer_info = []

            return {
                'stream_length': stream_info.get('length', 0),
                'groups': len(group_info),
                'consumers': len(consumer_info),
                'last_generated_id': stream_info.get('last-generated-id', '0-0')
            }

        except Exception as e:
            logger.error(f"Error getting queue stats: {e}")
            return {}

    async def clear_queue(self):
        """Clear all messages from the queue"""
        try:
            await self.redis.delete(realtime_config.redis_stream_key)
            logger.info("Queue cleared")
        except Exception as e:
            logger.error(f"Error clearing queue: {e}")

class WebSocketBroadcaster:
    """Handles WebSocket broadcasting of processed articles"""

    def __init__(self):
        self.connected_clients: set = set()
        self.redis = None

    async def connect_redis(self):
        """Connect to Redis for pub/sub or use mock"""
        if REDIS_AVAILABLE and realtime_config.redis_enabled:
            self.redis = redis.Redis(
                host=realtime_config.redis_host,
                port=realtime_config.redis_port,
                db=realtime_config.redis_db,
                decode_responses=True
            )
        else:
            self.redis = MockRedis()

    async def broadcast_article(self, article: Dict[str, Any]):
        """Broadcast article to all connected WebSocket clients"""
        message = {
            'type': 'new_article',
            'data': article,
            'timestamp': asyncio.get_event_loop().time()
        }

        # Remove disconnected clients
        disconnected = set()
        for client in self.connected_clients:
            try:
                await client.send_json(message)
            except Exception:
                disconnected.add(client)

        # Clean up disconnected clients
        self.connected_clients -= disconnected

        if disconnected:
            logger.info(f"Removed {len(disconnected)} disconnected clients")

    def add_client(self, websocket):
        """Add a new WebSocket client"""
        self.connected_clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.connected_clients)}")

    def remove_client(self, websocket):
        """Remove a WebSocket client"""
        self.connected_clients.discard(websocket)
        logger.info(f"Client disconnected. Total clients: {len(self.connected_clients)}")

# Global instances
queue_manager = QueueManager()
websocket_broadcaster = WebSocketBroadcaster()

async def initialize_queue_system():
    """Initialize the queue system"""
    await queue_manager.connect()
    await websocket_broadcaster.connect_redis()

async def shutdown_queue_system():
    """Shutdown the queue system"""
    queue_manager.stop_processing()
    await queue_manager.disconnect()

if __name__ == "__main__":
    # Test the queue manager
    async def test():
        await initialize_queue_system()

        # Test enqueuing
        test_article = {
            'title': 'Test Article',
            'content': 'This is a test article for the queue system.',
            'url': 'https://example.com/test'
        }

        message_id = await queue_manager.enqueue_article(test_article)
        print(f"Enqueued article with ID: {message_id}")

        # Get stats
        stats = await queue_manager.get_queue_stats()
        print(f"Queue stats: {stats}")

        await shutdown_queue_system()

    asyncio.run(test())
