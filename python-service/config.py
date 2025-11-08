import os
from typing import List, Dict

# Database configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', '../.wrangler/state/v3/d1/miniflare-D1DatabaseObject/0a63475064ba0fef38489ee0454cb2d789b28a906ef12161e40ea6ea13385173.sqlite')

# AI/ML Model configurations
SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
TRANSLATION_MODEL = "ai4bharat/indictrans2-en-indic-1B"  # For future implementation
LANGUAGE_DETECTION_MODEL = "langdetect"

# RSS Feed sources for Indian government news - UPDATED WORKING FEEDS
RSS_SOURCES = [
    {
        "name": "PIB Press Releases",
        "url": "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1",
        "language": "en",
        "region": "National",
        "category": "Government Press Release"
    },
    {
        "name": "The Hindu - Politics",
        "url": "https://www.thehindu.com/news/national/feeder/default.rss",
        "language": "en",
        "region": "National",
        "category": "Politics"
    },
    {
        "name": "Economic Times - Government",
        "url": "https://economictimes.indiatimes.com/news/economy/policy/rssfeeds/1373380680.cms",
        "language": "en",
        "region": "National",
        "category": "Economy & Finance"
    },
    {
        "name": "Hindustan Times - India",
        "url": "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",
        "language": "en",
        "region": "National",
        "category": "General"
    },
    {
        "name": "Indian Express - India",
        "url": "https://indianexpress.com/section/india/feed/",
        "language": "en",
        "region": "National",
        "category": "General"
    },
    {
        "name": "Times of India - India",
        "url": "https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms",
        "language": "en",
        "region": "National",
        "category": "General"
    },
    {
        "name": "NDTV - India",
        "url": "https://feeds.feedburner.com/ndtvnews-india-news",
        "language": "en",
        "region": "National",
        "category": "General"
    },
    {
        "name": "News18 India",
        "url": "https://www.news18.com/rss/india.xml",
        "language": "en",
        "region": "National",
        "category": "General"
    },
    {
        "name": "Zee News - India",
        "url": "https://zeenews.india.com/rss/india-national-news.xml",
        "language": "en",
        "region": "National",
        "category": "General"
    },
    {
        "name": "Aaj Tak - National",
        "url": "https://www.aajtak.in/rssfeeds/rssfeed-1.xml",
        "language": "hi",
        "region": "National",
        "category": "General"
    }
]

# Government-related keywords for filtering
GOVERNMENT_KEYWORDS = [
    # English keywords
    "government", "minister", "ministry", "parliament", "lok sabha", "rajya sabha",
    "prime minister", "chief minister", "governor", "policy", "scheme", "budget",
    "central government", "state government", "cabinet", "bjp", "congress", "election",
    "democracy", "legislation", "bill", "act", "supreme court", "high court",

    # Hindi keywords (transliterated)
    "sarkar", "mantri", "pradhan mantri", "mukhya mantri", "rajyapal", "niti",
    "yojana", "budget", "sansad", "chunav", "kanoon", "adhiniyam",

    # Common across languages
    "modi", "amit shah", "rahul gandhi", "pib", "press information bureau",
    "india", "bharat", "delhi", "mumbai", "kolkata", "chennai", "bangalore"
]

# Sentiment thresholds for alerts
NEGATIVE_SENTIMENT_THRESHOLD = -0.3
CRITICAL_SENTIMENT_THRESHOLD = -0.7

# Processing configuration
FETCH_INTERVAL_MINUTES = 30
MAX_ARTICLES_PER_FETCH = 50
BATCH_SIZE = 10

# Regional mapping for language detection
LANGUAGE_REGION_MAP = {
    "en": "National",
    "hi": "North India",
    "ta": "South India",
    "te": "South India",
    "kn": "South India",
    "ml": "South India",
    "bn": "East India",
    "gu": "West India",
    "mr": "West India",
    "pa": "North India",
    "ur": "North India"
}

# Category classification keywords
CATEGORY_KEYWORDS = {
    "Healthcare & Pandemic": [
        "health", "hospital", "covid", "pandemic", "vaccine", "medicine", "doctor",
        "swasthya", "aspatal", "dawai", "tikakaran"
    ],
    "Education": [
        "education", "school", "college", "university", "student", "teacher", "exam",
        "shiksha", "vidyalaya", "mahavidyalaya", "vishwavidyalaya", "chatra", "adhyapak"
    ],
    "Infrastructure": [
        "infrastructure", "road", "bridge", "railway", "airport", "highway", "metro",
        "sadak", "pul", "rel", "havai adda", "rajmarg"
    ],
    "Agriculture": [
        "agriculture", "farmer", "crop", "farming", "rural", "krishi", "kisan",
        "fasal", "kheti", "grameen"
    ],
    "Economy & Finance": [
        "economy", "finance", "budget", "tax", "gst", "bank", "investment",
        "arthvyavastha", "vitaay", "kar", "bank", "nivesh"
    ],
    "Defense & Security": [
        "defense", "army", "navy", "air force", "security", "border", "military",
        "raksha", "sena", "nausena", "vayu sena", "suraksha", "seema"
    ],
    "Environment & Climate": [
        "environment", "climate", "pollution", "forest", "wildlife", "green",
        "paryavaran", "jalvayu", "pradushan", "van", "jangali jeev"
    ],
    "Technology & Innovation": [
        "technology", "digital", "internet", "innovation", "startup", "ai",
        "takneek", "digital", "internet", "navachar"
    ]
}
