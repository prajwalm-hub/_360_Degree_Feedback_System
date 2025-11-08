#!/usr/bin/env python3

import os
import logging
from database import DatabaseManager
from rss_collector import RSSCollector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_environment():
    """Set up the environment for the news monitoring service"""
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    logger.info("Created logs directory")
    
    # Initialize database
    db = DatabaseManager()
    logger.info("Database connection established")
    
    # Initialize RSS sources
    collector = RSSCollector(db)
    collector.initialize_rss_sources()
    logger.info("RSS sources initialized")
    
    # Sample data insertion removed as requested
    
    logger.info("Setup completed successfully!")

# Sample data insertion function removed as requested

if __name__ == "__main__":
    setup_environment()
