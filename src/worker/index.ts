import { Hono } from "hono";
import { zValidator } from '@hono/zod-validator';
import { cors } from 'hono/cors';
import { 
  NewsArticleSchema
} from '../shared/types';

const app = new Hono<{ Bindings: Env }>();

// Enable CORS
app.use('*', cors());

// Health check endpoint
app.get('/health', (c) => {
  return c.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// Get dashboard statistics
app.get('/api/dashboard/stats', async (c) => {
  try {
    const db = c.env.DB;
    
    // Get total articles
    const totalArticlesResult = await db.prepare('SELECT COUNT(*) as count FROM news_articles').first();
    const totalArticles = totalArticlesResult?.count || 0;
    
    // Get sentiment distribution
    const sentimentResult = await db.prepare(`
      SELECT 
        sentiment_label,
        COUNT(*) as count
      FROM news_articles 
      WHERE sentiment_label IS NOT NULL
      GROUP BY sentiment_label
    `).all();
    
    const sentimentDistribution = {
      positive: 0,
      negative: 0,
      neutral: 0
    };
    
    sentimentResult.results?.forEach((row: any) => {
      if (row.sentiment_label && sentimentDistribution.hasOwnProperty(row.sentiment_label)) {
        sentimentDistribution[row.sentiment_label as keyof typeof sentimentDistribution] = row.count;
      }
    });
    
    // Get recent alerts
    const alertsResult = await db.prepare(`
      SELECT * FROM alerts 
      WHERE is_read = 0 
      ORDER BY created_at DESC 
      LIMIT 5
    `).all();
    
    // Get trending topics (simplified - just categories for now)
    const topicsResult = await db.prepare(`
      SELECT category, COUNT(*) as count
      FROM news_articles 
      WHERE category IS NOT NULL 
        AND created_at >= date('now', '-7 days')
      GROUP BY category
      ORDER BY count DESC
      LIMIT 5
    `).all();
    
    const trendingTopics = topicsResult.results?.map((row: any) => row.category) || [];
    
    // Get regional coverage
    const regionalResult = await db.prepare(`
      SELECT 
        region,
        COUNT(*) as count,
        AVG(sentiment_score) as avg_sentiment
      FROM news_articles 
      WHERE region IS NOT NULL
      GROUP BY region
      ORDER BY count DESC
    `).all();
    
    const regionalCoverage = regionalResult.results?.map((row: any) => ({
      region: row.region,
      count: row.count,
      sentiment: row.avg_sentiment || 0
    })) || [];
    
    const stats = {
      total_articles: totalArticles,
      total_sources: 0, // Will be calculated when we add sources
      total_languages: 0, // Will be calculated when we add language tracking
      sentiment_distribution: sentimentDistribution,
      recent_alerts: alertsResult.results || [],
      trending_topics: trendingTopics,
      regional_coverage: regionalCoverage
    };
    
    return c.json({ success: true, data: stats });
  } catch (error) {
    console.error('Dashboard stats error:', error);
    return c.json({ success: false, error: 'Failed to fetch dashboard statistics' }, 500);
  }
});

// Get news articles with filtering
app.get('/api/articles', async (c) => {
  try {
    const db = c.env.DB;
    const { category, region, sentiment, language, limit = '20', offset = '0' } = c.req.query();
    
    let query = 'SELECT * FROM news_articles WHERE 1=1';
    const params: any[] = [];
    
    if (category) {
      query += ' AND category = ?';
      params.push(category);
    }
    
    if (region) {
      query += ' AND region = ?';
      params.push(region);
    }
    
    if (sentiment) {
      query += ' AND sentiment_label = ?';
      params.push(sentiment);
    }
    
    if (language) {
      query += ' AND language = ?';
      params.push(language);
    }
    
    query += ' ORDER BY publish_date DESC, created_at DESC LIMIT ? OFFSET ?';
    params.push(parseInt(limit), parseInt(offset));
    
    const result = await db.prepare(query).bind(...params).all();
    
    return c.json({ success: true, data: result.results });
  } catch (error) {
    console.error('Articles fetch error:', error);
    return c.json({ success: false, error: 'Failed to fetch articles' }, 500);
  }
});

// Add news article (for testing/demo purposes)
app.post('/api/articles', zValidator('json', NewsArticleSchema), async (c) => {
  try {
    const db = c.env.DB;
    const article = c.req.valid('json');
    
    const now = new Date().toISOString();
    
    const result = await db.prepare(`
      INSERT INTO news_articles (
        title, content, source, source_url, language, translated_content,
        author, publish_date, region, category, sentiment_score, sentiment_label,
        emotions, keywords, summary, entities, is_government_related, created_at, updated_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).bind(
      article.title,
      article.content,
      article.source,
      article.source_url || null,
      article.language,
      article.translated_content || null,
      article.author || null,
      article.publish_date || now,
      article.region || null,
      article.category || null,
      article.sentiment_score || null,
      article.sentiment_label || null,
      article.emotions || null,
      article.keywords || null,
      article.summary || null,
      article.entities || null,
      article.is_government_related ? 1 : 0,
      now,
      now
    ).run();
    
    return c.json({ success: true, data: { id: result.meta.last_row_id } });
  } catch (error) {
    console.error('Article creation error:', error);
    return c.json({ success: false, error: 'Failed to create article' }, 500);
  }
});

// Get sentiment analytics
app.get('/api/analytics/sentiment', async (c) => {
  try {
    const db = c.env.DB;
    const { days = '7' } = c.req.query();
    
    const result = await db.prepare(`
      SELECT 
        DATE(publish_date) as date,
        category,
        sentiment_label,
        COUNT(*) as count,
        AVG(sentiment_score) as avg_score
      FROM news_articles 
      WHERE publish_date >= date('now', '-' || ? || ' days')
        AND sentiment_label IS NOT NULL
      GROUP BY DATE(publish_date), category, sentiment_label
      ORDER BY date DESC
    `).bind(parseInt(days)).all();
    
    return c.json({ success: true, data: result.results });
  } catch (error) {
    console.error('Sentiment analytics error:', error);
    return c.json({ success: false, error: 'Failed to fetch sentiment analytics' }, 500);
  }
});

// Get government entities
app.get('/api/entities', async (c) => {
  try {
    const db = c.env.DB;
    
    const result = await db.prepare(`
      SELECT * FROM government_entities 
      ORDER BY mentions_count DESC 
      LIMIT 50
    `).all();
    
    return c.json({ success: true, data: result.results });
  } catch (error) {
    console.error('Entities fetch error:', error);
    return c.json({ success: false, error: 'Failed to fetch entities' }, 500);
  }
});

// Get alerts
app.get('/api/alerts', async (c) => {
  try {
    const db = c.env.DB;
    const { unread_only = 'false' } = c.req.query();
    
    let query = 'SELECT * FROM alerts';
    if (unread_only === 'true') {
      query += ' WHERE is_read = 0';
    }
    query += ' ORDER BY created_at DESC LIMIT 100';
    
    const result = await db.prepare(query).all();
    
    return c.json({ success: true, data: result.results });
  } catch (error) {
    console.error('Alerts fetch error:', error);
    return c.json({ success: false, error: 'Failed to fetch alerts' }, 500);
  }
});

// Mark alert as read
app.patch('/api/alerts/:id/read', async (c) => {
  try {
    const db = c.env.DB;
    const alertId = c.req.param('id');

    await db.prepare(`
      UPDATE alerts
      SET is_read = 1, updated_at = ?
      WHERE id = ?
    `).bind(new Date().toISOString(), alertId).run();

    return c.json({ success: true });
  } catch (error) {
    console.error('Alert update error:', error);
    return c.json({ success: false, error: 'Failed to update alert' }, 500);
  }
});

// Reset database (remove demo articles)
app.post('/api/reset', async (c) => {
  try {
    const db = c.env.DB;

    // Delete demo articles (keeping only live news from RSS feeds)
    const demoSources = ['Test Source', 'PIB', 'Economic Times', 'Health Ministry', 'Construction News'];
    const placeholders = demoSources.map(() => '?').join(',');

    await db.prepare(`
      DELETE FROM news_articles
      WHERE source IN (${placeholders})
    `).bind(...demoSources).run();

    // Also clean up related analytics and alerts for demo data
    await db.prepare('DELETE FROM sentiment_analytics').run();
    await db.prepare('DELETE FROM alerts').run();
    await db.prepare('DELETE FROM government_entities').run();

    return c.json({
      success: true,
      message: 'Demo data removed successfully',
      demo_sources_removed: demoSources
    });
  } catch (error) {
    console.error('Database reset error:', error);
    return c.json({ success: false, error: 'Failed to reset database' }, 500);
  }
});

// Python service integration endpoints
app.post('/api/python/collect-news', async (c) => {
  try {
    // Call the Python service API running on localhost:8000
    const response = await fetch('http://localhost:8000/collect-news', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Python service returned ${response.status}`);
    }

    const data = await response.json();
    return c.json(data);
  } catch (error) {
    console.error('Python service call error:', error);
    return c.json({
      success: false,
      error: 'Failed to trigger news collection. Make sure Python service is running on port 8000.'
    }, 500);
  }
});

app.post('/api/python/process-articles', async (c) => {
  try {
    // Call the Python service API running on localhost:8000
    const response = await fetch('http://localhost:8000/process-articles', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Python service returned ${response.status}`);
    }

    const data = await response.json();
    return c.json(data);
  } catch (error) {
    console.error('Python service call error:', error);
    return c.json({
      success: false,
      error: 'Failed to trigger article processing. Make sure Python service is running on port 8000.'
    }, 500);
  }
});

app.post('/api/python/run-cycle', async (c) => {
  try {
    // Call the Python service API running on localhost:8000
    const response = await fetch('http://localhost:8000/run-cycle', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Python service returned ${response.status}`);
    }

    const data = await response.json();
    return c.json(data);
  } catch (error) {
    console.error('Python service call error:', error);
    return c.json({
      success: false,
      error: 'Failed to trigger processing cycle. Make sure Python service is running on port 8000.'
    }, 500);
  }
});

app.get('/api/python/status', async (c) => {
  try {
    const db = c.env.DB;

    // Get processing jobs status - since we don't have processing_jobs table yet,
    // simulate with article processing status based on recent articles
    const recentArticlesResult = await db.prepare(`
      SELECT
        CASE
          WHEN created_at >= datetime('now', '-1 hour') THEN 'processing'
          WHEN created_at >= datetime('now', '-24 hours') THEN 'completed'
          ELSE 'completed'
        END as status,
        COUNT(*) as count
      FROM news_articles
      WHERE created_at >= datetime('now', '-24 hours')
      GROUP BY
        CASE
          WHEN created_at >= datetime('now', '-1 hour') THEN 'processing'
          WHEN created_at >= datetime('now', '-24 hours') THEN 'completed'
          ELSE 'completed'
        END
    `).all();

    // Get active RSS sources count - simulate based on configured sources
    // For now, return a count based on recent article sources
    const sourcesResult = await db.prepare(`
      SELECT COUNT(DISTINCT source) as active_sources
      FROM news_articles
      WHERE created_at >= datetime('now', '-7 days')
    `).all();

    // Transform the results to match expected format
    const jobStatistics = [
      { status: 'pending', count: 0 },
      { status: 'processing', count: 0 },
      { status: 'completed', count: 0 },
      { status: 'failed', count: 0 }
    ];

    recentArticlesResult.results?.forEach((row: any) => {
      const statusIndex = jobStatistics.findIndex(job => job.status === row.status);
      if (statusIndex !== -1) {
        jobStatistics[statusIndex].count = row.count;
      }
    });

    // Calculate completed articles (older articles are considered completed)
    const totalArticlesResult = await db.prepare(`
      SELECT COUNT(*) as total
      FROM news_articles
    `).first();

    const totalArticles = totalArticlesResult?.total || 0;
    const recentArticles = recentArticlesResult.results?.reduce((sum: number, row: any) => sum + row.count, 0) || 0;

    // Add to completed count (articles older than 24h are completed)
    const completedIndex = jobStatistics.findIndex(job => job.status === 'completed');
    if (completedIndex !== -1) {
      jobStatistics[completedIndex].count = Math.max(0, totalArticles - recentArticles);
    }

    return c.json({
      success: true,
      data: {
        job_statistics: jobStatistics,
        active_sources: sourcesResult.results?.[0]?.active_sources || 0,
        timestamp: new Date().toISOString()
      }
    });
  } catch (error) {
    console.error('Python service status error:', error);
    return c.json({ success: false, error: 'Failed to get service status' }, 500);
  }
});

export default app;
