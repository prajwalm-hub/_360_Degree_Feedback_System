# NewsScope India - Complete Setup and API Guide

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Installation Steps](#installation-steps)
4. [Running the Project](#running-the-project)
5. [API Documentation](#api-documentation)
6. [Database Information](#database-information)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

**NewsScope India** is a multilingual news monitoring platform that:
- Collects news from 13 Indian languages (English, Hindi, Kannada, Tamil, Telugu, Bengali, Malayalam, Marathi, Gujarati, Punjabi, Odia, Urdu, Assamese)
- Automatically translates regional language content to English
- Performs sentiment analysis on news articles
- Provides analytics and alerts for government-related news
- Uses RSS feeds and web scraping for data collection

**Technology Stack:**
- **Backend:** Python 3.10 + FastAPI + PostgreSQL
- **Frontend:** React + TypeScript + Vite
- **AI/ML:** Translation, Sentiment Analysis, Entity Extraction
- **Database:** PostgreSQL with SQLAlchemy ORM

---

## 📦 Prerequisites

### Required Software

1. **Python 3.10**
   - Download from: https://www.python.org/downloads/
   - ✅ Already installed on your system

2. **PostgreSQL Database**
   - Download from: https://www.postgresql.org/download/
   - ✅ Already installed and running

3. **Node.js (v16 or higher)**
   - Download from: https://nodejs.org/
   - Required for frontend

4. **Git** (optional)
   - For version control

### Database Configuration
```
Host: localhost
Port: 5432
Database: newsdb
Username: postgres
Password: praju
```

---

## 🚀 Installation Steps

### Step 1: Install Backend Dependencies

```powershell
# Navigate to backend folder
cd "c:\Users\prajwal m\Downloads\NewsScope_India_Fixed\backend"

# Install Python packages
py -3.10 -m pip install -r requirements.txt

# Install translation libraries
py -3.10 -m pip install googletrans==4.0.0rc1
py -3.10 -m pip install deep-translator
```

### Step 2: Install Frontend Dependencies

```powershell
# Navigate to frontend folder
cd "c:\Users\prajwal m\Downloads\NewsScope_India_Fixed\frontend"

# Install Node.js packages
npm install
```

### Step 3: Setup Database Tables

```powershell
# Navigate to backend folder
cd "c:\Users\prajwal m\Downloads\NewsScope_India_Fixed\backend"

# Create database tables
$env:DATABASE_URL="postgresql+psycopg2://postgres:praju@localhost:5432/newsdb"
py -3.10 create_tables.py
```

### Step 4: Initialize Admin User (Optional)

```powershell
cd "c:\Users\prajwal m\Downloads\NewsScope_India_Fixed\backend"
$env:DATABASE_URL="postgresql+psycopg2://postgres:praju@localhost:5432/newsdb"
py -3.10 init_admin.py
```

**Default Admin Credentials:**
- Email: `admin@newsscope.in`
- Password: `admin123`

---

## ▶️ Running the Project

### Method 1: Using Batch Files (Easiest)

#### Start Backend Server
```powershell
cd "c:\Users\prajwal m\Downloads\NewsScope_India_Fixed"
.\START-BACKEND-8001.bat
```
✅ Backend will run on: **http://localhost:8000**

#### Start Frontend Server
Open a **new PowerShell window**:
```powershell
cd "c:\Users\prajwal m\Downloads\NewsScope_India_Fixed"
.\start-frontend.bat
```
✅ Frontend will run on: **http://localhost:5173** or **http://localhost:5174**

### Method 2: Manual Commands

#### Start Backend (Terminal 1)
```powershell
cd "c:\Users\prajwal m\Downloads\NewsScope_India_Fixed\backend"
$env:DATABASE_URL="postgresql+psycopg2://postgres:praju@localhost:5432/newsdb"
$env:NLP_ENABLED="false"
$env:TRANSLATION_ENABLED="true"
py -3.10 run_server.py
```

#### Start Frontend (Terminal 2)
```powershell
cd "c:\Users\prajwal m\Downloads\NewsScope_India_Fixed\frontend"
npm run dev
```

### Verify Everything is Running

1. **Backend API:** Open browser → http://localhost:8000/docs
   - You should see FastAPI Swagger documentation

2. **Frontend UI:** Open browser → http://localhost:5173 or http://localhost:5174
   - You should see the NewsScope dashboard

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication Endpoints

#### 1. Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "admin@newsscope.in",
  "password": "admin123"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "admin@newsscope.in",
    "full_name": "Admin User"
  }
}
```

#### 2. Register New User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe"
}
```

### News Articles Endpoints

#### 3. Get All News Articles
```http
GET /api/news?skip=0&limit=20&language=en

Query Parameters:
- skip: number (pagination offset, default: 0)
- limit: number (items per page, default: 20)
- language: string (filter by language code: en, hi, kn, etc.)

Response:
{
  "items": [
    {
      "id": 1,
      "title": "Article Title",
      "translated_title": "Translated Title",
      "content": "Article content...",
      "translated_content": "Translated content...",
      "url": "https://example.com/article",
      "language": "hi",
      "source_name": "Amar Ujala",
      "published_at": "2025-11-06T10:30:00",
      "sentiment_score": 0.75,
      "sentiment_label": "positive",
      "created_at": "2025-11-06T10:35:00"
    }
  ],
  "total": 1000,
  "skip": 0,
  "limit": 20
}
```

#### 4. Get Single Article by ID
```http
GET /api/news/{article_id}

Response:
{
  "id": 1,
  "title": "Article Title",
  "translated_title": "Translated Title",
  "content": "Full article content...",
  "translated_content": "Translated content...",
  "url": "https://example.com/article",
  "language": "hi",
  "source_name": "Amar Ujala",
  "published_at": "2025-11-06T10:30:00",
  "sentiment_score": 0.75,
  "sentiment_label": "positive",
  "entities": ["Government", "PM Modi", "Parliament"],
  "created_at": "2025-11-06T10:35:00"
}
```

#### 5. Search News Articles
```http
GET /api/news/search?q=parliament&limit=10

Query Parameters:
- q: string (search query)
- limit: number (max results, default: 10)

Response:
{
  "results": [
    {
      "id": 1,
      "title": "Parliament Session Today",
      "translated_title": "Parliament Session Today",
      "score": 0.95
    }
  ],
  "total": 5
}
```

### Analytics Endpoints

#### 6. Get Language Distribution
```http
GET /api/analytics/languages

Response:
{
  "languages": [
    {
      "language": "en",
      "count": 632,
      "percentage": 42.3
    },
    {
      "language": "or",
      "count": 300,
      "percentage": 20.1
    },
    {
      "language": "hi",
      "count": 153,
      "percentage": 10.2
    }
  ],
  "total_articles": 1000
}
```

#### 7. Get Sentiment Distribution
```http
GET /api/analytics/sentiment

Response:
{
  "sentiment": [
    {
      "label": "positive",
      "count": 450,
      "percentage": 45.0
    },
    {
      "label": "neutral",
      "count": 350,
      "percentage": 35.0
    },
    {
      "label": "negative",
      "count": 200,
      "percentage": 20.0
    }
  ],
  "average_score": 0.62
}
```

#### 8. Get Daily Article Trends
```http
GET /api/analytics/trends?days=7

Query Parameters:
- days: number (number of days to analyze, default: 7)

Response:
{
  "trends": [
    {
      "date": "2025-11-06",
      "count": 150,
      "sentiment_avg": 0.65
    },
    {
      "date": "2025-11-05",
      "count": 120,
      "sentiment_avg": 0.58
    }
  ]
}
```

#### 9. Get Source Statistics
```http
GET /api/analytics/sources

Response:
{
  "sources": [
    {
      "source_name": "The Hindu",
      "count": 250,
      "language": "en"
    },
    {
      "source_name": "Sambad",
      "count": 200,
      "language": "or"
    }
  ]
}
```

#### 10. Get Top Entities
```http
GET /api/analytics/entities?limit=10

Response:
{
  "entities": [
    {
      "name": "PM Modi",
      "count": 450,
      "type": "PERSON"
    },
    {
      "name": "Parliament",
      "count": 320,
      "type": "ORGANIZATION"
    }
  ]
}
```

### Alerts & Notifications

#### 11. Get User Alerts
```http
GET /api/alerts/notifications
Authorization: Bearer {access_token}

Response:
{
  "alerts": [
    {
      "id": 1,
      "title": "New Article Alert",
      "message": "10 new articles from PIB India",
      "priority": "medium",
      "is_read": false,
      "created_at": "2025-11-06T10:00:00"
    }
  ],
  "unread_count": 5
}
```

#### 12. Mark Alert as Read
```http
PUT /api/alerts/{alert_id}/read
Authorization: Bearer {access_token}

Response:
{
  "message": "Alert marked as read"
}
```

### Data Collection Endpoints

#### 13. Trigger RSS Collection
```http
POST /api/collection/rss/trigger
Authorization: Bearer {access_token}

Response:
{
  "message": "RSS collection started",
  "task_id": "abc123"
}
```

#### 14. Check Collection Status
```http
GET /api/collection/status

Response:
{
  "last_run": "2025-11-06T09:00:00",
  "articles_collected": 121,
  "status": "completed"
}
```

### Statistics Endpoints

#### 15. Get Overall Statistics
```http
GET /api/stats

Response:
{
  "total_articles": 1000,
  "total_sources": 26,
  "languages_covered": 13,
  "last_updated": "2025-11-06T10:00:00",
  "articles_today": 150,
  "sentiment_breakdown": {
    "positive": 450,
    "neutral": 350,
    "negative": 200
  }
}
```

---

## 🗄️ Database Information

### Connection String
```
postgresql+psycopg2://postgres:praju@localhost:5432/newsdb
```

### Main Tables

#### 1. `articles` Table
Stores all news articles with multilingual content.

**Columns:**
- `id` (Primary Key)
- `title` (Original title)
- `translated_title` (English translation)
- `content` (Original content)
- `translated_content` (English translation)
- `url` (Article URL)
- `language` (Language code: en, hi, kn, etc.)
- `source_name` (RSS feed source)
- `published_at` (Publication date)
- `sentiment_score` (Float: -1 to 1)
- `sentiment_label` (positive/neutral/negative)
- `created_at` (When added to DB)

#### 2. `users` Table
User authentication and profiles.

**Columns:**
- `id` (Primary Key)
- `email` (Unique)
- `hashed_password`
- `full_name`
- `is_active`
- `created_at`

#### 3. `alerts` Table
User notifications and alerts.

**Columns:**
- `id` (Primary Key)
- `user_id` (Foreign Key to users)
- `title`
- `message`
- `priority` (low/medium/high)
- `is_read`
- `created_at`

### Query Database Directly

```powershell
# Connect to PostgreSQL
psql -U postgres -d newsdb

# Example queries:
SELECT COUNT(*) FROM articles;
SELECT language, COUNT(*) FROM articles GROUP BY language;
SELECT * FROM articles WHERE language = 'hi' LIMIT 5;
```

---

## 🔧 Data Collection

### Run RSS Feed Collection

```powershell
cd "c:\Users\prajwal m\Downloads\NewsScope_India_Fixed\backend"
$env:DATABASE_URL="postgresql+psycopg2://postgres:praju@localhost:5432/newsdb"
py -3.10 run_rss_collector.py
```

This will:
- Fetch articles from 26 RSS feeds (2 per language)
- Automatically detect language
- Translate non-English content to English
- Perform sentiment analysis
- Store in database

### Monitor Collection

```powershell
cd "c:\Users\prajwal m\Downloads\NewsScope_India_Fixed\backend"
$env:DATABASE_URL="postgresql+psycopg2://postgres:praju@localhost:5432/newsdb"
py -3.10 monitor_collection.py
```

### Check Language Statistics

```powershell
cd "c:\Users\prajwal m\Downloads\NewsScope_India_Fixed\backend"
$env:DATABASE_URL="postgresql+psycopg2://postgres:praju@localhost:5432/newsdb"
py -3.10 check_language_stats.py
```

---

## 🛠️ Troubleshooting

### Problem 1: Backend Not Starting

**Error:** "Address already in use" or "Port 8000 is busy"

**Solution:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace XXXX with PID)
Stop-Process -Id XXXX -Force

# Restart backend
cd "c:\Users\prajwal m\Downloads\NewsScope_India_Fixed\backend"
py -3.10 run_server.py
```

### Problem 2: Frontend Shows "Failed to fetch"

**Cause:** Backend not running or CORS issue

**Solution:**
1. Verify backend is running: http://localhost:8000/docs
2. Check frontend proxy in `vite.config.ts`:
   ```typescript
   proxy: {
     '/api': {
       target: 'http://localhost:8000',
       changeOrigin: true
     }
   }
   ```

### Problem 3: Database Connection Error

**Error:** "could not connect to server"

**Solution:**
1. Check PostgreSQL service is running:
   ```powershell
   # Check status
   Get-Service postgresql*
   
   # Start if stopped
   Start-Service postgresql-x64-XX
   ```

2. Verify credentials:
   ```
   Host: localhost
   Port: 5432
   Database: newsdb
   User: postgres
   Password: praju
   ```

### Problem 4: No Articles Collected

**Possible Causes:**
- RSS feeds are down
- Network connectivity issue
- Database write permissions

**Solution:**
```powershell
# Test RSS feeds
cd "c:\Users\prajwal m\Downloads\NewsScope_India_Fixed\backend"
$env:DATABASE_URL="postgresql+psycopg2://postgres:praju@localhost:5432/newsdb"
py -3.10 test_regional_feeds.py

# Check database
SELECT COUNT(*) FROM articles;
```

### Problem 5: Translation Not Working

**Cause:** Translation libraries not installed or API limits

**Solution:**
```powershell
# Reinstall translation libraries
py -3.10 -m pip install --upgrade googletrans==4.0.0rc1
py -3.10 -m pip install --upgrade deep-translator

# Check translation is enabled
$env:TRANSLATION_ENABLED="true"
```

---

## 📚 Additional Resources

### Configuration Files

1. **Backend Config:** `backend/app/config.py`
   - Database URL
   - API settings
   - Feature flags (NLP, Translation)

2. **RSS Feeds:** `backend/app/feeds.yaml`
   - 26 curated RSS feeds
   - 2 per language (National + Regional)

3. **Frontend Config:** `frontend/vite.config.ts`
   - Dev server settings
   - Proxy configuration

### Environment Variables

```powershell
# Required for backend
$env:DATABASE_URL="postgresql+psycopg2://postgres:praju@localhost:5432/newsdb"

# Optional features
$env:NLP_ENABLED="false"          # Enable/disable NLP processing
$env:TRANSLATION_ENABLED="true"   # Enable/disable translation
```

### Supported Languages

| Code | Language | Script | Status |
|------|----------|--------|--------|
| en | English | Latin | ✅ Active |
| hi | Hindi | Devanagari | ✅ Active |
| kn | Kannada | Kannada | ✅ Active |
| ta | Tamil | Tamil | ✅ Active |
| te | Telugu | Telugu | ✅ Active |
| bn | Bengali | Bengali | ✅ Active |
| ml | Malayalam | Malayalam | ✅ Active |
| mr | Marathi | Devanagari | ✅ Active |
| gu | Gujarati | Gujarati | ✅ Active |
| pa | Punjabi | Gurmukhi | ✅ Active |
| or | Odia | Odia | ✅ Active |
| ur | Urdu | Arabic | ✅ Active |
| as | Assamese | Bengali | ✅ Active |

---

## 🎉 Quick Start Checklist

- [ ] PostgreSQL running on localhost:5432
- [ ] Python 3.10 installed
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Database tables created (`py -3.10 create_tables.py`)
- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:5173 or 5174
- [ ] Can access API docs at http://localhost:8000/docs
- [ ] Can access UI at http://localhost:5173

---

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Check terminal output for error messages
4. Ensure PostgreSQL service is running
5. Verify network connectivity for RSS feeds

**Project Structure:**
```
NewsScope_India_Fixed/
├── backend/              # Python FastAPI backend
│   ├── app/             # Main application code
│   ├── collectors/      # RSS and web scrapers
│   ├── ai_pipeline/     # Translation & NLP
│   └── requirements.txt # Python dependencies
├── frontend/            # React frontend
│   ├── src/            # Source code
│   ├── package.json    # Node dependencies
│   └── vite.config.ts  # Vite configuration
└── docs/               # Documentation

```

---

**Last Updated:** November 6, 2025  
**Version:** 1.0  
**Status:** Production Ready ✅
