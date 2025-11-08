# Government News Monitor - Python AI/ML Service

This Python service provides real-time RSS feed collection, AI/ML processing for sentiment analysis, language detection, translation, and classification of government news articles.

## Features

- **RSS Feed Collection**: Collects news from 10+ regional Indian media sources
- **Language Detection**: Automatically detects article language using `langdetect`
- **Sentiment Analysis**: Uses Hugging Face transformers for sentiment classification
- **Content Translation**: Placeholder for IndicTrans2 integration
- **Article Classification**: Categorizes articles by government department
- **Real-time Alerts**: Generates alerts for negative sentiment and critical keywords
- **Entity Extraction**: Identifies government entities and officials

## Setup

### Prerequisites

- Python 3.8+
- pip
- SQLite3

### Installation

1. Navigate to the python-service directory:
```bash
cd python-service
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the environment:
```bash
python setup.py
```

## Usage

### Command Line Interface

Run different components independently:

```bash
# Collect news from RSS feeds
python main.py collect

# Process pending articles with AI/ML
python main.py process

# Run a complete collection and processing cycle
python main.py cycle

# Run with scheduler (continuous operation)
python main.py
```

### API Server

Start the FastAPI server for integration:

```bash
python api_server.py
```

The API will be available at `http://localhost:8000`

### API Endpoints

- `POST /api/collect-news` - Trigger news collection
- `POST /api/process-articles` - Trigger AI/ML processing
- `POST /api/run-cycle` - Run complete cycle
- `GET /api/job-status` - Get processing job status
- `GET /api/sources` - Get RSS sources
- `GET /api/statistics` - Get processing statistics

## Configuration

### RSS Sources

The system monitors these Indian news sources:

- PIB Press Releases (English)
- The Hindu - Politics (English)
- Economic Times - Government (English)
- Dainik Jagran (Hindi)
- Anandabazar Patrika (Bengali)
- Dinamalar (Tamil)
- Eenadu (Telugu)
- Prajavani (Kannada)
- Gujarat Samachar (Gujarati)
- Loksatta (Marathi)

### AI/ML Models

- **Sentiment Analysis**: `cardiffnlp/twitter-roberta-base-sentiment-latest`
- **Language Detection**: `langdetect`
- **Translation**: IndicTrans2 (to be integrated)

### Processing Pipeline

1. **Collection**: RSS feeds are fetched every 30 minutes
2. **Filtering**: Articles are filtered for government relevance
3. **Language Detection**: Article language is automatically detected
4. **Translation**: Non-English content is translated (placeholder)
5. **Sentiment Analysis**: Sentiment scores and labels are assigned
6. **Classification**: Articles are categorized by department
7. **Entity Extraction**: Government entities are identified
8. **Alert Generation**: Alerts are created for negative sentiment

## Database Schema

The service uses the existing SQLite database with additional tables:

- `rss_sources` - RSS feed sources configuration
- `processing_jobs` - Background job tracking
- `news_articles` - Enhanced with AI/ML fields
- `alerts` - Real-time alert system

## Integration with Cloudflare Worker

The Python service integrates with the existing Cloudflare Worker through:

1. **Shared Database**: Both services use the same SQLite database
2. **API Endpoints**: Worker has endpoints to trigger Python processing
3. **Real-time Updates**: Dashboard updates automatically with processed data

## Monitoring and Logging

- Logs are written to `logs/news_monitor.log`
- Processing statistics are available via API
- Job status tracking for monitoring pipeline health

## Future Enhancements

1. **IndicTrans2 Integration**: Full translation capability for regional languages
2. **Advanced NER**: Named Entity Recognition for government officials
3. **Trend Analysis**: Historical sentiment trends and anomaly detection
4. **Advanced Categorization**: Machine learning-based department classification
5. **Real-time Streaming**: WebSocket integration for live updates

## Troubleshooting

### Common Issues

1. **Model Loading Errors**: Ensure sufficient memory and stable internet for downloading models
2. **RSS Feed Timeouts**: Check network connectivity and RSS source availability
3. **Database Locks**: Ensure only one instance is running for write operations

### Performance Optimization

- Batch processing for better throughput
- Model caching to reduce loading time
- Database connection pooling
- Async processing for non-blocking operations

## License

This project is part of the Government News Monitoring System for demonstration purposes.
