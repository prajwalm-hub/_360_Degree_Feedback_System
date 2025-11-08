# Clean Sentiment Analysis Page Code

## Complete working code for SentimentAnalysisPage.tsx

**Instructions:**
1. Delete the corrupted `frontend/src/react-app/pages/SentimentAnalysisPage.tsx`
2. Create a new file with this content:

```typescript
import { useState } from 'react';
import { useApi } from '@/react-app/hooks/useApi';
import { NewsArticle } from '@/shared/types';
import { TrendingUp, TrendingDown, Minus, Loader2, RefreshCw, Filter } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';

interface SentimentData {
  sentiment: Array<{
    label: string;
    count: number;
    percentage: number;
  }>;
  average_score: number;
}

interface LanguageData {
  languages: Array<{
    language: string;
    count: number;
  }>;
}

export default function SentimentAnalysisPage() {
  const [selectedLanguage, setSelectedLanguage] = useState<string>('all');
  const [timeRange, setTimeRange] = useState<number>(7);
  
  const { data: sentimentData, loading: sentimentLoading } = useApi<SentimentData>('/analytics/sentiment');
  const { data: languageData } = useApi<LanguageData>('/analytics/languages');
  const { data: articlesData, loading: articlesLoading } = useApi<{ items: NewsArticle[]; total: number }>(
    selectedLanguage === 'all' ? '/news?limit=10' : `/news?language=${selectedLanguage}&limit=10`
  );

  const handleRefresh = () => {
    window.location.reload();
  };

  if (sentimentLoading || articlesLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-2 text-gray-600">
          <Loader2 className="w-6 h-6 animate-spin" />
          <span>Loading sentiment analysis...</span>
        </div>
      </div>
    );
  }

  const sentimentChartData = sentimentData?.sentiment?.map(item => ({
    name: item.label.charAt(0).toUpperCase() + item.label.slice(1),
    value: item.count,
    percentage: item.percentage
  })) || [];

  const COLORS = {
    'Positive': '#10b981',
    'Neutral': '#6b7280',
    'Negative': '#ef4444'
  };

  const getSentimentBadge = (score: number | null | undefined) => {
    if (score === null || score === undefined) return { label: 'Unknown', className: 'bg-gray-100 text-gray-800' };
    if (score > 0.2) return { label: 'Positive', className: 'bg-green-100 text-green-800' };
    if (score < -0.2) return { label: 'Negative', className: 'bg-red-100 text-red-800' };
    return { label: 'Neutral', className: 'bg-gray-100 text-gray-800' };
  };

  const getSentimentIcon = (score: number | null | undefined) => {
    if (score === null || score === undefined) return <Minus className="w-4 h-4" />;
    if (score > 0.2) return <TrendingUp className="w-4 h-4 text-green-600" />;
    if (score < -0.2) return <TrendingDown className="w-4 h-4 text-red-600" />;
    return <Minus className="w-4 h-4 text-gray-600" />;
  };

  const positiveCount = sentimentData?.sentiment?.find(s => s.label === 'positive')?.count || 0;
  const neutralCount = sentimentData?.sentiment?.find(s => s.label === 'neutral')?.count || 0;
  const negativeCount = sentimentData?.sentiment?.find(s => s.label === 'negative')?.count || 0;
  const totalArticles = positiveCount + neutralCount + negativeCount;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <TrendingUp className="w-8 h-8 mr-3 text-green-600" />
            Sentiment Analysis
          </h1>
          <p className="text-gray-600 mt-1">Monitor public sentiment trends across government news coverage</p>
        </div>
        <button
          onClick={handleRefresh}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Refresh</span>
        </button>
      </div>

      <div className="bg-white rounded-xl p-4 border border-gray-200">
        <div className="flex items-center space-x-4">
          <Filter className="w-5 h-5 text-gray-600" />
          <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Language</label>
              <select
                value={selectedLanguage}
                onChange={(e) => setSelectedLanguage(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Languages</option>
                {languageData?.languages?.map((lang) => (
                  <option key={lang.language} value={lang.language}>
                    {lang.language.toUpperCase()} ({lang.count} articles)
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Time Range</label>
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value={1}>Last 24 hours</option>
                <option value={7}>Last 7 days</option>
                <option value={30}>Last 30 days</option>
                <option value={90}>Last 90 days</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Articles</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{totalArticles}</p>
            </div>
            <div className="p-3 rounded-lg bg-blue-100">
              <TrendingUp className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Positive</p>
              <p className="text-3xl font-bold text-green-600 mt-1">{positiveCount}</p>
              <p className="text-sm text-gray-500 mt-1">
                {totalArticles > 0 ? Math.round((positiveCount / totalArticles) * 100) : 0}%
              </p>
            </div>
            <div className="p-3 rounded-lg bg-green-100">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Neutral</p>
              <p className="text-3xl font-bold text-gray-600 mt-1">{neutralCount}</p>
              <p className="text-sm text-gray-500 mt-1">
                {totalArticles > 0 ? Math.round((neutralCount / totalArticles) * 100) : 0}%
              </p>
            </div>
            <div className="p-3 rounded-lg bg-gray-100">
              <Minus className="w-6 h-6 text-gray-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Negative</p>
              <p className="text-3xl font-bold text-red-600 mt-1">{negativeCount}</p>
              <p className="text-sm text-gray-500 mt-1">
                {totalArticles > 0 ? Math.round((negativeCount / totalArticles) * 100) : 0}%
              </p>
            </div>
            <div className="p-3 rounded-lg bg-red-100">
              <TrendingDown className="w-6 h-6 text-red-600" />
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Sentiment Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={sentimentChartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(entry: { name: string; percentage: number }) => `${entry.name}: ${entry.percentage.toFixed(1)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {sentimentChartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[entry.name as keyof typeof COLORS]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Sentiment Count</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={sentimentChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-white rounded-xl p-6 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Analyzed Articles (Top 10)</h3>
        {articlesData && articlesData.items && articlesData.items.length > 0 ? (
          <div className="space-y-3">
            {articlesData.items.map((article) => {
              const sentiment = getSentimentBadge(article.sentiment_score);
              return (
                <div key={article.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        {getSentimentIcon(article.sentiment_score)}
                        <h4 className="font-medium text-gray-900">{article.translated_title || article.title}</h4>
                      </div>
                      <p className="text-sm text-gray-600 line-clamp-2">
                        {article.summary || (article.content || '').substring(0, 150) + '...'}
                      </p>
                      <div className="flex items-center space-x-4 mt-3 text-xs text-gray-500">
                        <span className="flex items-center">
                          <span className="font-medium mr-1">Language:</span>
                          {article.language?.toUpperCase() || 'N/A'}
                        </span>
                        {article.source && (
                          <span className="flex items-center">
                            <span className="font-medium mr-1">Source:</span>
                            {article.source}
                          </span>
                        )}
                        {typeof article.sentiment_score === 'number' && (
                          <span className="flex items-center">
                            <span className="font-medium mr-1">Score:</span>
                            {article.sentiment_score.toFixed(3)}
                          </span>
                        )}
                      </div>
                    </div>
                    <span className={`ml-4 px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap ${sentiment.className}`}>
                      {sentiment.label}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">No articles found</p>
        )}
      </div>
    </div>
  );
}
```

## Usage Instructions:

1. **Delete corrupted file:**
```powershell
cd "c:\Users\prajwal m\Downloads\NewsScope_India_Fixed\frontend\src\react-app\pages"
Remove-Item SentimentAnalysisPage.tsx -Force
```

2. **Create new file** and paste the code above

3. **Test the build:**
```powershell
cd "c:\Users\prajwal m\Downloads\NewsScope_India_Fixed\frontend"
npm run dev
```

4. **Navigate to Sentiment Analysis** page in the browser to verify it works

## Expected Features:

✅ 4 metric cards (Total, Positive, Neutral, Negative) with icons  
✅ Language filter dropdown populated from API  
✅ Time range selector (24h, 7d, 30d, 90d)  
✅ Pie chart showing sentiment distribution with percentages  
✅ Bar chart showing sentiment counts  
✅ List of 10 recent articles with color-coded sentiment badges  
✅ Each article shows: title, summary, language, source, sentiment score  
✅ Responsive design for mobile/tablet/desktop  
✅ Hover effects on article cards  
✅ Refresh button to reload data  

## Dependencies Required (Already Installed):

- recharts: ^3.2.1 ✅
- lucide-react: ^0.510.0 ✅
- react: 19.0.0 ✅

All set! The page should work perfectly once you replace the corrupted file.
