# RAG Assistant Implementation Guide

## Overview

The RAG (Retrieval-Augmented Generation) Assistant is an intelligent Q&A system integrated into NewsScope India that allows users to ask questions about government news in natural language across 11+ Indian languages.

## Features

### 🎯 Core Capabilities
- **Multilingual Question Answering**: Ask questions in English, Hindi, and other Indian languages
- **Real-time News Retrieval**: Search through thousands of recent government news articles
- **Source Attribution**: Every answer includes links to original news sources
- **Sentiment-Aware**: Filter by positive, negative, or neutral news
- **Ministry & Scheme Focused**: Query specific government ministries and schemes
- **Confidence Scoring**: AI provides confidence levels for answers

### 📊 Smart Features
- **Quick Insights**: Dashboard showing trending topics, sentiment distribution, and active ministries
- **Query Suggestions**: Pre-built question templates in multiple languages
- **Contextual Understanding**: Understands GoI-specific terminology and entities
- **Date Filtering**: Query news from specific time periods
- **Aggregated Summaries**: Get summaries by topic, ministry, or scheme

## Architecture

```
┌─────────────────┐
│   User Query    │
│  (Multilingual) │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│      RAG Assistant Pipeline         │
│  1. Translation (if needed)         │
│  2. Embedding Generation            │
│  3. Vector Similarity Search        │
│  4. Document Retrieval              │
│  5. Answer Generation               │
│  6. Source Attribution              │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│      Vector Store (FAISS)           │
│  - Article Embeddings               │
│  - Metadata (ministry, sentiment)   │
│  - Multilingual Support             │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│    PostgreSQL Database              │
│  - Full Articles                    │
│  - Translations                     │
│  - Entity Annotations               │
└─────────────────────────────────────┘
```

## Installation

### 1. Backend Dependencies

Update your Python environment:

```bash
cd backend
pip install -r requirements.txt
```

New dependencies added:
- `langchain==0.1.0` - Core RAG framework
- `langchain-community==0.0.13` - Community integrations
- `langchain-openai==0.0.5` - OpenAI integration (optional)
- `faiss-cpu==1.7.4` - Vector similarity search
- `chromadb==0.4.22` - Alternative vector store
- `tiktoken==0.5.2` - Token counting
- `openai==1.10.0` - OpenAI API (optional)

### 2. Environment Variables

Add to your `.env` file:

```bash
# Optional: OpenAI API for better answers (recommended for production)
OPENAI_API_KEY=your_api_key_here

# RAG Configuration
RAG_EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-mpnet-base-v2
RAG_CACHE_DIR=./vector_cache
RAG_DEFAULT_DAYS=30
RAG_K_DOCUMENTS=5
```

### 3. Database Preparation

The RAG system uses existing article data. Ensure your database has recent articles:

```bash
# Run news collection
python backend/collect_news_enhanced.py
```

### 4. Build Vector Store

Initialize the vector store (first time only):

```bash
# Option 1: Via API (recommended)
curl -X POST http://localhost:8000/api/rag/build \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"days": 30, "force_rebuild": false}'

# Option 2: Via Python
python -c "
from backend.app.database import get_database
from backend.app.rag_assistant import get_rag_assistant

db = get_database()
rag = get_rag_assistant(db)
rag.build_vectorstore(days=30)
print('Vector store built successfully!')
"
```

## API Endpoints

### 1. Query RAG Assistant

**POST** `/api/rag/query`

Ask a question and get an AI-generated answer with sources.

```json
{
  "question": "Summarize today's news about PM Modi",
  "language": "en",
  "k": 5,
  "filters": {
    "sentiment": "positive",
    "is_goi": true,
    "ministries": ["Ministry of Finance"]
  }
}
```

Response:
```json
{
  "answer": "Recent news highlights PM Modi's address on economic reforms...",
  "sources": [
    {
      "article_id": "abc123",
      "url": "https://...",
      "source": "PIB",
      "published_at": "2024-11-05T10:30:00",
      "language": "en",
      "sentiment": "positive",
      "ministries": ["PMO"],
      "schemes": []
    }
  ],
  "confidence": 0.85,
  "retrieved_docs": 5,
  "language": "en"
}
```

### 2. Build Vector Store

**POST** `/api/rag/build`

Build or rebuild the vector store from recent articles.

```json
{
  "days": 30,
  "filters": {
    "is_goi": true,
    "language": "hi"
  },
  "force_rebuild": false
}
```

### 3. Get Status

**GET** `/api/rag/status`

Check if RAG system is ready.

```json
{
  "initialized": true,
  "last_update": "2024-11-05T12:00:00",
  "embedding_model": "multilingual",
  "cache_dir": "./vector_cache"
}
```

### 4. Quick Insights

**GET** `/api/rag/quick-insights?days=7`

Get aggregated statistics from recent news.

```json
{
  "period_days": 7,
  "date_from": "2024-10-29T00:00:00",
  "top_topics": [
    ["Economic Policy", 45],
    ["Health Schemes", 32],
    ["Digital India", 28]
  ],
  "sentiment_distribution": {
    "positive": 120,
    "neutral": 85,
    "negative": 15
  },
  "top_ministries": [
    ["Ministry of Finance", 38],
    ["Ministry of Health", 25]
  ]
}
```

### 5. Get Suggestions

**GET** `/api/rag/suggestions?language=en`

Get pre-built question suggestions.

```json
{
  "suggestions": [
    "Summarize today's news about the Prime Minister",
    "What are the latest government schemes announced?",
    "Show me positive news about Jal Jeevan Mission"
  ],
  "language": "en"
}
```

### 6. Get Summary

**POST** `/api/rag/summary`

Get aggregated summaries by topic, sentiment, or ministry.

```json
{
  "filters": {
    "date_from": "2024-11-01",
    "language": "hi",
    "sentiment": "positive"
  },
  "summary_type": "ministries"
}
```

## Frontend Integration

### Add to Router

Update your `App.tsx` or router configuration:

```tsx
import AssistantPage from './pages/AssistantPage';

// In your routes
<Route path="/assistant" element={<AssistantPage />} />
```

### Add to Navigation

Update your navigation menu:

```tsx
{
  name: 'AI Assistant',
  icon: Sparkles,
  path: '/assistant',
  description: 'Ask questions about government news'
}
```

### Standalone Component

Use the RAG Assistant component anywhere:

```tsx
import RAGAssistant from '../components/RAGAssistant';

function MyPage() {
  return (
    <div className="h-screen">
      <RAGAssistant 
        apiBaseUrl="/api"
        language="en"
        onLanguageChange={(lang) => console.log('Language changed:', lang)}
      />
    </div>
  );
}
```

## Example Queries

### English Queries
```
1. "Summarize today's news about PM Modi"
2. "What are the latest government schemes announced?"
3. "Show me positive news about Jal Jeevan Mission"
4. "What did the Finance Minister say recently?"
5. "Summarize news about digital India initiatives"
6. "What's happening with railway modernization?"
7. "Show me news about Ayushman Bharat scheme"
8. "What are the trending topics in government news?"
```

### Hindi Queries
```
1. "प्रधानमंत्री के बारे में आज की खबरों का सारांश दें"
2. "हाल ही में घोषित सरकारी योजनाएं क्या हैं?"
3. "जल जीवन मिशन के बारे में सकारात्मक समाचार दिखाएं"
4. "वित्त मंत्री ने हाल ही में क्या कहा?"
5. "डिजिटल इंडिया पहल के बारे में समाचारों का सारांश दें"
```

## Advanced Features

### 1. Metadata Filtering

Filter results by various criteria:

```python
filters = {
    "language": "hi",           # Hindi only
    "sentiment": "positive",     # Positive news only
    "is_goi": True,             # Government news only
    "ministries": ["Ministry of Health"],
    "date_from": "2024-11-01",
    "date_to": "2024-11-05"
}
```

### 2. Custom Embeddings

Use OpenAI embeddings for better performance:

```python
rag = RAGAssistant(
    db=db,
    use_openai=True,  # Requires OPENAI_API_KEY
    embedding_model="text-embedding-ada-002"
)
```

### 3. Scheduled Vector Store Updates

Add to your cron or scheduler:

```python
from apscheduler.schedulers.background import BackgroundScheduler

def update_vectorstore():
    db = get_database()
    rag = get_rag_assistant(db)
    rag.build_vectorstore(days=30, force_rebuild=True)

scheduler = BackgroundScheduler()
scheduler.add_job(update_vectorstore, 'cron', hour=2)  # Daily at 2 AM
scheduler.start()
```

### 4. Performance Optimization

For production deployments:

1. **Use GPU for embeddings**:
   ```python
   embeddings = HuggingFaceEmbeddings(
       model_name="...",
       model_kwargs={'device': 'cuda'}
   )
   ```

2. **Cache frequently asked questions**:
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=100)
   def cached_query(question: str):
       return rag.query(question)
   ```

3. **Use ChromaDB for persistence**:
   ```python
   from langchain_community.vectorstores import Chroma
   
   vectorstore = Chroma(
       collection_name="newsscope",
       embedding_function=embeddings,
       persist_directory="./chroma_db"
   )
   ```

## Troubleshooting

### Vector Store Not Initialized

**Error**: "Vector store not initialized"

**Solution**:
```bash
curl -X POST http://localhost:8000/api/rag/build \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"days": 30}'
```

### Out of Memory Errors

**Error**: "CUDA out of memory" or "Memory allocation failed"

**Solutions**:
1. Use CPU instead of GPU
2. Reduce chunk size in text splitter
3. Process fewer articles (reduce `days` parameter)
4. Use smaller embedding model

### Slow Query Performance

**Solutions**:
1. Build vector store with fewer documents
2. Reduce `k` parameter (number of retrieved documents)
3. Use OpenAI embeddings instead of local models
4. Enable GPU acceleration
5. Use FAISS with IVF index for large datasets

### No Results Found

**Solutions**:
1. Check if vector store contains data: `GET /api/rag/status`
2. Rebuild vector store with broader filters
3. Try simpler queries
4. Check article collection is running

## Performance Benchmarks

Typical performance on standard hardware:

| Operation | Time | Notes |
|-----------|------|-------|
| Build vector store (10k articles) | 2-5 min | One-time operation |
| Query (5 docs) | 0.5-2 sec | Depends on model |
| Query with OpenAI | 1-3 sec | Network latency |
| Embedding generation | 100-200 ms | Per query |

## Security Considerations

1. **Authentication**: All endpoints require valid JWT token
2. **Rate Limiting**: Implement rate limiting for query endpoint
3. **API Keys**: Store OpenAI API keys in environment variables
4. **Input Validation**: Questions are validated and sanitized
5. **CORS**: Configure allowed origins in production

## Future Enhancements

Planned features:
- [ ] Conversation history and context
- [ ] Multi-turn dialogue support
- [ ] Voice input/output
- [ ] Advanced analytics dashboard
- [ ] Custom fine-tuned models
- [ ] Integration with government databases
- [ ] Real-time news streaming
- [ ] Automated fact-checking
- [ ] Multi-modal support (images, videos)

## Support

For issues or questions:
1. Check logs: `backend/logs/rag.log`
2. Review API documentation: `http://localhost:8000/docs`
3. Test endpoints with Swagger UI
4. Check vector store cache: `./vector_cache/`

## License

Same as NewsScope India project.
