#!/usr/bin/env python3

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import logging

import sys
import os
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'models'))
from models.database_models import DatabaseManager, Article, Video, SocialMediaPost, Entity, Topic, SentimentAnalytic, GovernmentFeedback, Alert
from rss_collector import RSSCollector
from ai_processor import AIProcessor
from models import JobStatus
from api.endpoints import router as api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Government News Monitor API", version="1.0.0")

# Include the API router
app.include_router(api_router, prefix="/api/v1")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
db_manager = DatabaseManager("sqlite:///../.wrangler/state/v3/d1/miniflare-D1DatabaseObject/0a63475064ba0fef38489ee0454cb2d789b28a906ef12161e40ea6ea13385173.sqlite")
ai_processor = AIProcessor()
rss_collector = RSSCollector(db_manager)

class ProcessingResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class JobStatusResponse(BaseModel):
    success: bool
    jobs: List[Dict[str, Any]]

@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    logger.info("Starting News Monitor API server...")
    # Initialize database tables
    db_manager.create_all_tables()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Government News Monitor API"}

@app.post("/api/collect-news")
async def collect_news(background_tasks: BackgroundTasks):
    """Trigger news collection from RSS sources"""
    try:
        # Run collection in background
        background_tasks.add_task(rss_collector.collect_news)

        return ProcessingResponse(
            success=True,
            message="News collection started",
            data={"status": "initiated"}
        )
    except Exception as e:
        logger.error(f"Error starting news collection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process-articles")
async def process_articles(background_tasks: BackgroundTasks):
    """Trigger AI/ML processing of pending articles"""
    try:
        # Run processing in background
        background_tasks.add_task(ai_processor.process_pending_articles)

        return ProcessingResponse(
            success=True,
            message="Article processing started",
            data={"status": "initiated"}
        )
    except Exception as e:
        logger.error(f"Error starting article processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/run-cycle")
async def run_cycle(background_tasks: BackgroundTasks):
    """Run a complete collection and processing cycle"""
    try:
        # Run complete cycle in background
        articles = rss_collector.collect_news()
        result = ai_processor.process_articles_batch(articles)

        return ProcessingResponse(
            success=True,
            message="Processing cycle completed",
            data=result
        )
    except Exception as e:
        logger.error(f"Error running processing cycle: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/job-status")
async def get_job_status():
    """Get status of processing jobs"""
    try:
        db = DatabaseManager()
        
        # Get recent jobs
        pending_jobs = db.get_pending_jobs()
        
        # Get job statistics
        job_stats = db.execute_query("""
            SELECT status, COUNT(*) as count 
            FROM processing_jobs 
            WHERE created_at >= datetime('now', '-24 hours')
            GROUP BY status
        """)
        
        return JobStatusResponse(
            success=True,
            jobs=[{
                "job_id": job.id,
                "job_type": job.job_type,
                "status": job.status.value,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "article_id": job.article_id
            } for job in pending_jobs],
        )
    except Exception as e:
        logger.error(f"Error getting job status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sources")
async def get_rss_sources():
    """Get RSS sources"""
    try:
        db = DatabaseManager()
        sources = db.get_active_rss_sources()
        
        return {
            "success": True,
            "data": [{
                "id": source.id,
                "name": source.name,
                "url": source.url,
                "language": source.language,
                "region": source.region,
                "category": source.category,
                "is_active": source.is_active,
                "last_fetched_at": source.last_fetched_at.isoformat() if source.last_fetched_at else None
            } for source in sources]
        }
    except Exception as e:
        logger.error(f"Error getting RSS sources: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/statistics")
async def get_statistics():
    """Get processing statistics"""
    try:
        db = DatabaseManager()
        
        # Get article counts by language
        lang_stats = db.execute_query("""
            SELECT language, COUNT(*) as count 
            FROM news_articles 
            GROUP BY language 
            ORDER BY count DESC
        """)
        
        # Get processing job stats
        job_stats = db.execute_query("""
            SELECT status, COUNT(*) as count 
            FROM processing_jobs 
            WHERE created_at >= datetime('now', '-24 hours')
            GROUP BY status
        """)
        
        # Get recent activity
        recent_articles = db.execute_query("""
            SELECT COUNT(*) as count 
            FROM news_articles 
            WHERE created_at >= datetime('now', '-1 hour')
        """)
        
        return {
            "success": True,
            "data": {
                "language_distribution": [{"language": row["language"], "count": row["count"]} for row in lang_stats],
                "job_status_distribution": [{"status": row["status"], "count": row["count"]} for row in job_stats],
                "recent_articles_count": recent_articles[0]["count"] if recent_articles else 0,
                "timestamp": db_manager.execute_query("SELECT datetime('now') as now")[0]["now"]
            }
        }
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
