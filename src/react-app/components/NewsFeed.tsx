import { useEffect, useState } from 'react';
import {
  Calendar,
  Globe,
  Tag,
  ExternalLink,
  Search,
  TrendingUp,
  TrendingDown,
  Minus,
  Wifi,
  WifiOff
} from 'lucide-react';
import type { NewsArticle } from '@/shared/types';
import { useWebSocket } from '../hooks/useWebSocket';

export default function NewsFeed() {
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    category: '',
    region: '',
    sentiment: '',
    language: '',
    search: '',
    governmentOnly: false,
    department: ''
  });

  // WebSocket integration
  const { isConnected, newsArticles: realtimeArticles, error: wsError } = useWebSocket('ws://localhost:8765');

  useEffect(() => {
    fetchArticles();
  }, [filters]);

  // Update articles when real-time articles arrive
  useEffect(() => {
    if (realtimeArticles.length > 0) {
      setArticles(prev => {
        // Merge real-time articles with existing ones, avoiding duplicates
        const existingKeys = new Set(prev.map(a => `${a.title}-${a.source}-${a.publish_date || ''}`));
        const newArticles = realtimeArticles.filter(a => !existingKeys.has(`${a.title}-${a.source}-${a.publish_date || ''}`));
        return [...newArticles, ...prev] as NewsArticle[];
      });
    }
  }, [realtimeArticles]);

  const fetchArticles = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();

      Object.entries(filters).forEach(([key, value]) => {
        if (value && key !== 'search' && key !== 'governmentOnly') {
          params.append(key, String(value));
        }
      });

      // Use government endpoint if governmentOnly is true
      const baseUrl = filters.governmentOnly ? '/api/articles/government/' : '/api/articles';
      const response = await fetch(`${baseUrl}?${params}`);
      const data = await response.json();

      if (data.success || !data.success) { // Handle both response formats
        let filteredArticles = data.data || data || [];

        // Apply search filter on frontend for now
        if (filters.search) {
          const searchTerm = filters.search.toLowerCase();
          filteredArticles = filteredArticles.filter((article: NewsArticle) =>
            article.title.toLowerCase().includes(searchTerm) ||
            article.content.toLowerCase().includes(searchTerm)
          );
        }

        setArticles(filteredArticles);
      }
    } catch (error) {
      console.error('Failed to fetch articles:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'negative':
        return <TrendingDown className="w-4 h-4 text-red-500" />;
      default:
        return <Minus className="w-4 h-4 text-gray-500" />;
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'negative':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold text-gray-900">News Feed</h1>
          <div className="flex items-center space-x-2">
            {isConnected ? (
              <Wifi className="w-5 h-5 text-green-500" />
            ) : (
              <WifiOff className="w-5 h-5 text-red-500" />
            )}
            <span className={`text-sm font-medium ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
              {isConnected ? 'Live' : 'Offline'}
            </span>
          </div>
        </div>
        
        {/* Search and Filters */}
        <div className="space-y-4">
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search articles..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Filter Dropdowns */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {/* Government Filter */}
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="governmentOnly"
                checked={filters.governmentOnly}
                onChange={(e) => setFilters({ ...filters, governmentOnly: e.target.checked })}
                className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="governmentOnly" className="text-sm font-medium text-gray-700">
                Government News Only
              </label>
            </div>

            <select
              value={filters.category}
              onChange={(e) => setFilters({ ...filters, category: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Categories</option>
              <option value="Policy & Legislation">Policy & Legislation</option>
              <option value="Healthcare & Pandemic">Healthcare & Pandemic</option>
              <option value="Education">Education</option>
              <option value="Infrastructure">Infrastructure</option>
              <option value="Economy & Finance">Economy & Finance</option>
              <option value="Defense & Security">Defense & Security</option>
              <option value="Environment & Climate">Environment & Climate</option>
              <option value="Agriculture">Agriculture</option>
              <option value="Technology & Innovation">Technology & Innovation</option>
              <option value="Social Welfare">Social Welfare</option>
            </select>

            <select
              value={filters.region}
              onChange={(e) => setFilters({ ...filters, region: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Regions</option>
              <option value="North India">North India</option>
              <option value="South India">South India</option>
              <option value="East India">East India</option>
              <option value="West India">West India</option>
              <option value="Central India">Central India</option>
              <option value="Northeast India">Northeast India</option>
            </select>

            <select
              value={filters.sentiment}
              onChange={(e) => setFilters({ ...filters, sentiment: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Sentiments</option>
              <option value="positive">Positive</option>
              <option value="neutral">Neutral</option>
              <option value="negative">Negative</option>
            </select>

            <select
              value={filters.language}
              onChange={(e) => setFilters({ ...filters, language: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Languages</option>
              <option value="en">English</option>
              <option value="hi">Hindi</option>
              <option value="ta">Tamil</option>
              <option value="te">Telugu</option>
              <option value="bn">Bengali</option>
              <option value="gu">Gujarati</option>
              <option value="kn">Kannada</option>
              <option value="ml">Malayalam</option>
              <option value="mr">Marathi</option>
              <option value="pa">Punjabi</option>
              <option value="ur">Urdu</option>
            </select>
          </div>

          {/* Department Filter - Show only when government news is selected */}
          {filters.governmentOnly && (
            <div className="mt-4">
              <select
                value={filters.department}
                onChange={(e) => setFilters({ ...filters, department: e.target.value })}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Departments</option>
                <option value="health">Health & Family Welfare</option>
                <option value="education">Education</option>
                <option value="finance">Finance</option>
                <option value="defence">Defence</option>
                <option value="agriculture">Agriculture</option>
                <option value="infrastructure">Infrastructure</option>
                <option value="environment">Environment & Climate</option>
                <option value="social_welfare">Social Welfare</option>
                <option value="technology">Technology</option>
                <option value="foreign_affairs">Foreign Affairs</option>
                <option value="home_affairs">Home Affairs</option>
                <option value="transport">Transport</option>
                <option value="commerce">Commerce</option>
                <option value="labour">Labour</option>
                <option value="law_justice">Law & Justice</option>
                <option value="petroleum">Petroleum</option>
                <option value="coal">Coal</option>
                <option value="new_renewable_energy">New & Renewable Energy</option>
                <option value="civil_aviation">Civil Aviation</option>
                <option value="heavy_industry">Heavy Industry</option>
                <option value="food_processing">Food Processing</option>
                <option value="textiles">Textiles</option>
                <option value="tourism">Tourism</option>
                <option value="youth_sports">Youth & Sports</option>
              </select>
            </div>
          )}
        </div>
      </div>

      {/* Articles List */}
      <div className="space-y-4">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
        ) : articles.length === 0 ? (
          <div className="bg-white rounded-xl p-12 text-center shadow-lg border border-gray-200">
            <p className="text-gray-500 text-lg">No articles found matching your criteria.</p>
            <p className="text-gray-400 text-sm mt-2">Try adjusting your filters or search terms.</p>
          </div>
        ) : (
          articles.map((article) => (
            <div key={article.id} className="bg-white rounded-xl p-6 shadow-lg border border-gray-200 hover:shadow-xl transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2 line-clamp-2">
                    {article.title}
                  </h3>
                  
                  <div className="flex flex-wrap items-center gap-4 mb-3">
                    {article.sentiment_label && (
                      <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium border ${getSentimentColor(article.sentiment_label)}`}>
                        {getSentimentIcon(article.sentiment_label)}
                        <span className="capitalize">{article.sentiment_label}</span>
                      </div>
                    )}
                    
                    {article.category && (
                      <div className="flex items-center space-x-1 px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                        <Tag className="w-3 h-3" />
                        <span>{article.category}</span>
                      </div>
                    )}
                    
                    {article.region && (
                      <div className="flex items-center space-x-1 px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium">
                        <Globe className="w-3 h-3" />
                        <span>{article.region}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <p className="text-gray-600 mb-4 line-clamp-3">
                {article.translated_content || article.content}
              </p>

              {article.summary && (
                <div className="bg-gray-50 rounded-lg p-3 mb-4">
                  <p className="text-sm text-gray-700 font-medium">Summary:</p>
                  <p className="text-sm text-gray-600 mt-1">{article.summary}</p>
                </div>
              )}

              <div className="flex items-center justify-between text-sm text-gray-500">
                <div className="flex items-center space-x-4">
                  <span className="font-medium text-gray-700">{article.source}</span>
                  {article.author && <span>by {article.author}</span>}
                  {article.publish_date && (
                    <div className="flex items-center space-x-1">
                      <Calendar className="w-4 h-4" />
                      <span>{formatDate(article.publish_date)}</span>
                    </div>
                  )}
                </div>
                
                {article.source_url && (
                  <a
                    href={article.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center space-x-1 text-blue-600 hover:text-blue-800 transition-colors"
                  >
                    <ExternalLink className="w-4 h-4" />
                    <span>Read Original</span>
                  </a>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
