import z from "zod";

// News Article Schema
export const NewsArticleSchema = z.object({
  id: z.number().optional(),
  title: z.string(),
  content: z.string(),
  source: z.string(),
  source_url: z.string().optional(),
  language: z.string(),
  translated_content: z.string().optional(),
  author: z.string().optional(),
  publish_date: z.string().optional(),
  region: z.string().optional(),
  category: z.string().optional(),
  sentiment_score: z.number().optional(),
  sentiment_label: z.enum(['positive', 'negative', 'neutral']).optional(),
  emotions: z.string().optional(),
  keywords: z.string().optional(),
  summary: z.string().optional(),
  entities: z.string().optional(),
  is_government_related: z.boolean().default(true),
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
});

export type NewsArticle = z.infer<typeof NewsArticleSchema>;

// Sentiment Analytics Schema
export const SentimentAnalyticsSchema = z.object({
  id: z.number().optional(),
  date: z.string(),
  category: z.string().optional(),
  region: z.string().optional(),
  language: z.string().optional(),
  positive_count: z.number().default(0),
  negative_count: z.number().default(0),
  neutral_count: z.number().default(0),
  avg_sentiment_score: z.number().optional(),
  total_articles: z.number().default(0),
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
});

export type SentimentAnalytics = z.infer<typeof SentimentAnalyticsSchema>;

// Government Entity Schema
export const GovernmentEntitySchema = z.object({
  id: z.number().optional(),
  name: z.string(),
  entity_type: z.string(),
  mentions_count: z.number().default(0),
  positive_mentions: z.number().default(0),
  negative_mentions: z.number().default(0),
  neutral_mentions: z.number().default(0),
  avg_sentiment: z.number().default(0),
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
});

export type GovernmentEntity = z.infer<typeof GovernmentEntitySchema>;

// Alert Schema
export const AlertSchema = z.object({
  id: z.number().optional(),
  alert_type: z.string(),
  severity: z.enum(['low', 'medium', 'high', 'critical']),
  title: z.string(),
  content: z.string(),
  article_id: z.number().optional(),
  threshold_triggered: z.number().optional(),
  is_read: z.boolean().default(false),
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
});

export type Alert = z.infer<typeof AlertSchema>;

// API Response Types
export const APIResponseSchema = z.object({
  success: z.boolean(),
  data: z.any().optional(),
  error: z.string().optional(),
  message: z.string().optional(),
});

export type APIResponse = z.infer<typeof APIResponseSchema>;

// Dashboard Statistics
export const DashboardStatsSchema = z.object({
  total_articles: z.number(),
  total_sources: z.number(),
  total_languages: z.number(),
  sentiment_distribution: z.object({
    positive: z.number(),
    negative: z.number(),
    neutral: z.number(),
  }),
  recent_alerts: z.array(AlertSchema),
  trending_topics: z.array(z.string()),
  regional_coverage: z.array(z.object({
    region: z.string(),
    count: z.number(),
    sentiment: z.number(),
  })),
});

export type DashboardStats = z.infer<typeof DashboardStatsSchema>;

// News Collection Request
export const NewsCollectionRequestSchema = z.object({
  sources: z.array(z.string()).optional(),
  languages: z.array(z.string()).optional(),
  categories: z.array(z.string()).optional(),
  keywords: z.array(z.string()).optional(),
  start_date: z.string().optional(),
  end_date: z.string().optional(),
});

export type NewsCollectionRequest = z.infer<typeof NewsCollectionRequestSchema>;

// Constants
export const SUPPORTED_LANGUAGES = [
  'en', 'hi', 'ta', 'te', 'bn', 'gu', 'kn', 'ml', 'mr', 'pa', 'ur'
] as const;

export const NEWS_CATEGORIES = [
  'Policy & Legislation',
  'Healthcare & Pandemic',
  'Education',
  'Infrastructure',
  'Economy & Finance',
  'Defense & Security',
  'Environment & Climate',
  'Agriculture',
  'Technology & Innovation',
  'Social Welfare',
  'General'
] as const;

export const INDIAN_REGIONS = [
  'North India',
  'South India',
  'East India',
  'West India',
  'Central India',
  'Northeast India'
] as const;
