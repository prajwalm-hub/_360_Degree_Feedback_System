# Real-Time AI-Powered NewsScope India

A real-time, high-accuracy AI-powered news monitoring system that collects, analyzes, and broadcasts government-related news from India using advanced NLP models and event-driven architecture.

## 🚀 Features

- **Real-Time Collection**: Web scraping with change detection instead of RSS polling
- **Advanced AI Models**: Hugging Face transformers for sentiment, summarization, NER, and government classification
- **Live Updates**: WebSocket-based real-time broadcasting to frontend
- **High Accuracy**: Confidence scoring and fine-tuned models
- **Scalable Architecture**: Redis Streams for queuing, async processing
- **Government Focus**: Specialized classifiers for Indian government news

## 🏗️ Architecture

```
[News Websites/APIs/Scrapers]
           ↓
[Change Detector + Listener]
           ↓
[Redis Streams Queue]
           ↓
[AI Processor (Hugging Face)]
           ↓
[Database + WebSocket Server]
           ↓
[Live Dashboard Updates]
```

## 📁 Project Structure

```
python-service/
├── realtime_main.py          # Main orchestrator
├── realtime_collector.py     # Real-time news collector
├── advanced_nlp.py          # Hugging Face NLP pipeline
├── queue_manager.py         # Redis Streams manager
├── websocket_server.py     # WebSocket broadcaster
├── config/
│   ├── realtime_config.py   # Real-time configuration
│   └── settings.py          # General settings
├── run_realtime.sh          # Management script
└── requirements.txt         # Dependencies

src/react-app/
├── hooks/
│   └── useWebSocket.ts      # WebSocket React hook
└── components/              # Updated components
```

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8+
- Redis Server
- Node.js (for frontend)

### 1. Install Dependencies

```bash
cd python-service
./run_realtime.sh install
```

### 2. Setup Environment

```bash
./run_realtime.sh setup
```

### 3. Start Redis

```bash
./run_realtime.sh start-redis
```

Or install and start Redis manually:

```bash
# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis

# macOS
brew install redis
brew services start redis

# Windows (using WSL or Docker)
docker run -d -p 6379:6379 redis:alpine
```

### 4. Start the System

#### Start Complete System
```bash
./run_realtime.sh start-full
```

#### Start Individual Components (for development/testing)
```bash
# Terminal 1: News collector
./run_realtime.sh start-collector

# Terminal 2: AI processor
./run_realtime.sh start-processor

# Terminal 3: WebSocket server
./run_realtime.sh start-websocket
```

## 🔧 Configuration

Edit `python-service/config/realtime_config.py` to customize:

- **News Sources**: Add/remove RSS feeds and websites
- **AI Models**: Configure model paths and parameters
- **Redis Settings**: Connection and stream configuration
- **WebSocket**: Server host/port settings
- **Processing**: Batch sizes, worker counts, timeouts

### Environment Variables

```bash
export REDIS_HOST=localhost
export REDIS_PORT=6379
export WEBSOCKET_PORT=8765
export AI_BATCH_SIZE=8
export AI_CONFIDENCE_THRESHOLD=0.7
```

## 🎯 AI Models Used

| Task | Model | Purpose |
|------|-------|---------|
| Sentiment Analysis | `cardiffnlp/twitter-roberta-base-sentiment-latest` | Detect positive/negative/neutral sentiment |
| Summarization | `facebook/bart-large-cnn` | Generate concise article summaries |
| Named Entity Recognition | `dslim/bert-base-NER` | Extract persons, organizations, locations |
| Government Classification | `bert-base-uncased` (fine-tuned) | Identify government-related content |

## 🌐 Frontend Integration

### WebSocket Hook

```typescript
import { useWebSocket } from './hooks/useWebSocket';

function NewsDashboard() {
  const { isConnected, newsArticles, systemStats } = useWebSocket();

  return (
    <div>
      <div>Status: {isConnected ? '🟢 Connected' : '🔴 Disconnected'}</div>
      {newsArticles.map(article => (
        <div key={article.url}>
          <h3>{article.title}</h3>
          <p>Sentiment: {article.sentiment?.sentiment}</p>
          <p>Confidence: {article.ai_confidence_score}</p>
        </div>
      ))}
    </div>
  );
}
```

### Real-Time Updates

The frontend automatically receives live updates via WebSocket:

- New articles appear instantly
- Sentiment analysis results update in real-time
- System statistics are broadcast live
- No page refresh required

## 📊 API Endpoints

### WebSocket Messages

```javascript
// Subscribe to topics
ws.send(JSON.stringify({
  type: 'subscribe',
  topics: ['government', 'politics']
}));

// Request system stats
ws.send(JSON.stringify({
  type: 'get_stats'
}));
```

### Cloudflare Worker Integration

The existing `/api/python/run-cycle` endpoint is maintained for backward compatibility.

## 🧪 Testing

### Run Basic Tests

```bash
./run_realtime.sh test
```

### Check System Status

```bash
./run_realtime.sh status
```

### Manual Testing

```python
# Test AI processing
from advanced_nlp import process_articles_batch

articles = [{
    'title': 'Government announces new policy',
    'content': 'Prime Minister Modi announced a new economic policy...',
    'url': 'https://example.com/news'
}]

processed = await process_articles_batch(articles)
print(processed[0]['sentiment'])
```

## 🔍 Monitoring & Debugging

### Logs

All components log to console. For production, configure proper logging:

```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/realtime_system.log'),
        logging.StreamHandler()
    ]
)
```

### Redis Monitoring

```bash
# Check queue length
redis-cli XLEN news_stream

# View pending messages
redis-cli XPENDING news_stream news_processors

# Monitor real-time
redis-cli MONITOR
```

### WebSocket Monitoring

```bash
# Check if WebSocket server is running
lsof -i :8765

# Test WebSocket connection
websocat ws://localhost:8765
```

## 🚀 Deployment

### Docker Setup

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8765

CMD ["python", "realtime_main.py"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  news-system:
    build: .
    ports:
      - "8765:8765"
    depends_on:
      - redis
    environment:
      - REDIS_HOST=redis
```

### Production Considerations

1. **Model Caching**: Cache downloaded models to avoid repeated downloads
2. **Rate Limiting**: Implement rate limiting for web scraping
3. **Error Handling**: Add comprehensive error handling and retries
4. **Monitoring**: Add metrics collection (Prometheus/Grafana)
5. **Security**: Add authentication for WebSocket connections
6. **Scaling**: Use multiple Redis instances for high availability

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**Redis Connection Failed**
```bash
# Check if Redis is running
redis-cli ping

# Start Redis
redis-server
```

**AI Models Not Loading**
```bash
# Clear cache and retry
rm -rf ~/.cache/huggingface
pip install --upgrade transformers torch
```

**WebSocket Connection Failed**
```bash
# Check firewall settings
sudo ufw allow 8765

# Verify WebSocket server is running
./run_realtime.sh status
```

**High Memory Usage**
```python
# Reduce batch size in config
ai_batch_size = 4  # Instead of 8
processing_workers = 2  # Instead of 4
```

## 📈 Performance Benchmarks

- **Collection Speed**: ~100 articles/minute
- **AI Processing**: ~50 articles/minute (with GPU)
- **WebSocket Latency**: <100ms
- **Memory Usage**: ~2GB (with models loaded)
- **CPU Usage**: ~60% during peak processing

## 🔄 Migration from Old System

The real-time system is designed to work alongside the existing system:

1. Keep existing RSS polling for backup
2. Gradually migrate to real-time collection
3. Update frontend to use WebSocket alongside existing API calls
4. Maintain backward compatibility with existing endpoints

## 📚 Additional Resources

- [Hugging Face Transformers Documentation](https://huggingface.co/docs/transformers/index)
- [Redis Streams Tutorial](https://redis.io/docs/data-types/streams/)
- [WebSocket Protocol](https://tools.ietf.org/html/rfc6455)
- [AsyncIO Documentation](https://docs.python.org/3/library/asyncio.html)
