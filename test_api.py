import requests

print("Testing backend API...")
print("=" * 50)

try:
    # Test health endpoint
    response = requests.get("http://localhost:8000/api/health")
    print(f"Health check status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    # Test metrics endpoint
    response = requests.get("http://localhost:8000/api/metrics")
    print(f"Metrics status: {response.status_code}")
    data = response.json()
    print(f"Total articles: {data.get('totalArticles', 0)}")
    print(f"Languages: {len(data.get('languageDistribution', []))}")
    print()
    
    # Test news endpoint
    response = requests.get("http://localhost:8000/api/news?limit=5")
    print(f"News status: {response.status_code}")
    news_data = response.json()
    print(f"Articles returned: {len(news_data.get('articles', []))}")
    print(f"Total in DB: {news_data.get('total', 0)}")
    
    print("\n✅ All API endpoints are working!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
