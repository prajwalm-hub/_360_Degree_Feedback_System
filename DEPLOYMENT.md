# Government News Monitor - Deployment Guide

This guide covers deploying the complete AI/ML-powered Government News Monitoring System with both the React dashboard and Python processing service.

## Architecture Overview

The system consists of two main components:

1. **Cloudflare Worker + React Dashboard**: Handles web interface and API endpoints
2. **Python AI/ML Service**: Handles RSS collection, sentiment analysis, and content processing

## Prerequisites

- Node.js 18+ and npm
- Python 3.8+
- SQLite3
- Cloudflare account (for production deployment)
- Docker (optional, for containerized deployment)

## Local Development Setup

### 1. Frontend (React Dashboard)

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The dashboard will be available at `http://localhost:5173`

### 2. Python AI/ML Service

```bash
# Navigate to python service directory
cd python-service

# Install dependencies
pip install -r requirements.txt

# Setup environment and database
python setup.py

# Start the API server
python api_server.py
```

The Python API will be available at `http://localhost:8000`

### 3. Running Both Services Together

**Terminal 1 (Frontend):**
```bash
npm run dev
```

**Terminal 2 (Python Service):**
```bash
cd python-service
./run.sh start-api
```

**Terminal 3 (Background Processing):**
```bash
cd python-service
./run.sh start
```

## Production Deployment

### Option 1: Cloud Deployment

#### Cloudflare Worker (Frontend)
```bash
# Build and deploy frontend
npm run build
npx wrangler deploy
```

#### Python Service (VPS/Cloud Server)
```bash
# On your server
git clone <your-repo>
cd government-news-monitor/python-service

# Install dependencies
pip install -r requirements.txt

# Setup environment
python setup.py

# Start with systemd (create service file)
sudo systemctl start news-monitor
sudo systemctl enable news-monitor
```

### Option 2: Docker Deployment

```bash
# Navigate to python service directory
cd python-service

# Build and start services
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

### Option 3: Complete Docker Setup

Create a `docker-compose.production.yml`:

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production

  python-api:
    build:
      context: ./python-service
    ports:
      - "8000:8000"
    volumes:
      - ./database:/app/database
      - ./logs:/app/logs
    restart: unless-stopped

  python-scheduler:
    build:
      context: ./python-service
    volumes:
      - ./database:/app/database
      - ./logs:/app/logs
    command: python main.py
    restart: unless-stopped
    depends_on:
      - python-api

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
    depends_on:
      - frontend
      - python-api
```

## Environment Configuration

### Python Service Environment Variables

```bash
# Database configuration
DATABASE_PATH=/path/to/database/db.sqlite

# AI/ML Model configuration
SENTIMENT_MODEL=cardiffnlp/twitter-roberta-base-sentiment-latest
HF_TOKEN=your_hugging_face_token  # Optional, for private models

# Processing configuration
FETCH_INTERVAL_MINUTES=30
MAX_ARTICLES_PER_FETCH=50
BATCH_SIZE=10

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/news_monitor.log
```

### Cloudflare Worker Environment

Set these in Cloudflare Dashboard or wrangler.toml:

```toml
[env.production]
vars = { PYTHON_SERVICE_URL = "https://your-python-service.com" }

[[env.production.d1_databases]]
binding = "DB"
database_name = "news-monitor-db"
database_id = "your-database-id"
```

## Systemd Service Configuration

Create `/etc/systemd/system/news-monitor-api.service`:

```ini
[Unit]
Description=Government News Monitor API
After=network.target

[Service]
Type=simple
User=newsmonitor
WorkingDirectory=/app/government-news-monitor/python-service
Environment=PATH=/app/venv/bin
ExecStart=/app/venv/bin/python api_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/news-monitor-scheduler.service`:

```ini
[Unit]
Description=Government News Monitor Scheduler
After=network.target

[Service]
Type=simple
User=newsmonitor
WorkingDirectory=/app/government-news-monitor/python-service
Environment=PATH=/app/venv/bin
ExecStart=/app/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable news-monitor-api news-monitor-scheduler
sudo systemctl start news-monitor-api news-monitor-scheduler
```

## Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Python API
    location /api/python/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Monitoring and Maintenance

### Health Checks

```bash
# Check frontend
curl http://localhost:5173/

# Check Python API
curl http://localhost:8000/

# Check processing status
curl http://localhost:8000/api/statistics
```

### Log Monitoring

```bash
# Python service logs
tail -f python-service/logs/news_monitor.log

# System logs
journalctl -u news-monitor-api -f
journalctl -u news-monitor-scheduler -f
```

### Database Maintenance

```bash
# Backup database
cp database/db.sqlite database/backup-$(date +%Y%m%d).sqlite

# Clean old processing jobs (older than 7 days)
sqlite3 database/db.sqlite "DELETE FROM processing_jobs WHERE created_at < datetime('now', '-7 days')"
```

## Performance Optimization

### Python Service

1. **Model Caching**: Models are cached in memory after first load
2. **Batch Processing**: Articles are processed in batches for efficiency
3. **Database Indexing**: Proper indexes are created for query performance
4. **Connection Pooling**: SQLite connection pooling for concurrent access

### Frontend

1. **Asset Optimization**: Vite handles bundling and optimization
2. **Code Splitting**: React Router handles lazy loading
3. **Caching**: Cloudflare provides global CDN caching

## Scaling Considerations

### Horizontal Scaling

1. **Multiple Python Workers**: Run multiple instances behind a load balancer
2. **Database Clustering**: Use PostgreSQL with read replicas for larger scale
3. **Message Queue**: Add Redis/RabbitMQ for job distribution
4. **Microservices**: Split RSS collection and AI processing into separate services

### Vertical Scaling

1. **GPU Support**: Enable CUDA for faster transformer models
2. **Memory Optimization**: Increase memory for larger models
3. **CPU Optimization**: Use multiple cores for parallel processing

## Security Considerations

1. **API Authentication**: Add JWT tokens for API access
2. **Rate Limiting**: Implement rate limiting for public endpoints
3. **HTTPS**: Use SSL certificates for secure communication
4. **Input Validation**: Validate all inputs and sanitize content
5. **Regular Updates**: Keep dependencies updated for security patches

## Troubleshooting

### Common Issues

1. **Model Loading Failures**: Check internet connection and HuggingFace access
2. **Database Lock Errors**: Ensure only one writer process at a time
3. **RSS Feed Timeouts**: Implement retry logic and timeout handling
4. **Memory Issues**: Monitor memory usage and implement model unloading

### Debug Commands

```bash
# Test RSS collection
cd python-service
python main.py collect

# Test AI processing
python main.py process

# Run single cycle
python main.py cycle

# Check service status
./run.sh status
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test locally
4. Submit a pull request with clear description

## License

This project is developed for demonstration purposes as part of the Government News Monitoring System.
