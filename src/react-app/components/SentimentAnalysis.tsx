import { useEffect, useState } from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  RefreshCw,
  Calendar,
  BarChart3,
  Newspaper,
  Settings
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';

interface SentimentData {
  positive: number;
  negative: number;
  neutral: number;
}

interface TrendData {
  date: string;
  positive: number;
  negative: number;
  neutral: number;
  total: number;
}

export default function SentimentAnalysis() {
  const [sentimentData, setSentimentData] = useState<SentimentData>({ positive: 0, negative: 0, neutral: 0 });
  const [trendData, setTrendData] = useState<TrendData[]>([]);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('24h');
  const [language, setLanguage] = useState('all');

  useEffect(() => {
    fetchSentimentData();
  }, [timeRange, language]);

  const fetchSentimentData = async () => {
    try {
      setLoading(true);
      
      // Get dashboard stats for sentiment distribution
      const statsResponse = await fetch('/api/v1/dashboard/stats/');
      const statsData = await statsResponse.json();
      
      if (statsData) {
        setSentimentData(statsData.sentiment_distribution || { positive: 0, negative: 0, neutral: 0 });
      }
      
      // Get sentiment analytics for trends
      const analyticsResponse = await fetch('/api/v1/sentiment_analytics/');
      const analyticsData = await analyticsResponse.json();
      
      if (analyticsData && Array.isArray(analyticsData)) {
        const processedTrends = processAnalyticsData(analyticsData);
        setTrendData(processedTrends);
      }
    } catch (error) {
      console.error('Failed to fetch sentiment data:', error);
    } finally {
      setLoading(false);
    }
  };

  const processAnalyticsData = (rawData: any[]): TrendData[] => {
    const dailyData: { [key: string]: TrendData } = {};
    
    rawData.forEach((item: any) => {
      const date = item.date;
      if (!dailyData[date]) {
        dailyData[date] = {
          date,
          positive: 0,
          negative: 0,
          neutral: 0,
          total: 0
        };
      }
      
      dailyData[date][item.sentiment_label as keyof Omit<TrendData, 'date' | 'total'>] += item.count;
      dailyData[date].total += item.count;
    });
    
    return Object.values(dailyData).sort((a, b) => a.date.localeCompare(b.date));
  };

  const totalSentiments = sentimentData.positive + sentimentData.negative + sentimentData.neutral;
  
  const getSentimentPercentage = (count: number) => {
    return totalSentiments > 0 ? Math.round((count / totalSentiments) * 100) : 0;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center">
              <Newspaper className="w-6 h-6 text-orange-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">NewsScope India</h1>
              <p className="text-sm text-gray-600">360° Regional News Monitoring</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <input
              type="text"
              placeholder="Search news articles..."
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-64"
            />
            <button className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center hover:bg-gray-200">
              <Settings className="w-5 h-5 text-gray-600" />
            </button>
            <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center text-white font-bold">
              A
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Language</label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Languages</option>
              <option value="en">English</option>
              <option value="hi">Hindi</option>
              <option value="kn">Kannada</option>
              <option value="ta">Tamil</option>
              <option value="te">Telugu</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Time Range</label>
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="24h">Last 24 hours</option>
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
            </select>
          </div>
        </div>
      </div>

      {/* Sentiment Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-green-100 rounded-xl flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-gray-600 text-sm font-medium">Positive Sentiment</p>
                <p className="text-2xl font-bold text-gray-900">{sentimentData.positive}</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-green-600 text-2xl font-bold">{getSentimentPercentage(sentimentData.positive)}%</p>
              <p className="text-gray-500 text-sm">of total</p>
            </div>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-green-500 h-2 rounded-full" 
              style={{ width: `${getSentimentPercentage(sentimentData.positive)}%` }}
            />
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gray-100 rounded-xl flex items-center justify-center">
                <Minus className="w-6 h-6 text-gray-600" />
              </div>
              <div>
                <p className="text-gray-600 text-sm font-medium">Neutral Sentiment</p>
                <p className="text-2xl font-bold text-gray-900">{sentimentData.neutral}</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-gray-600 text-2xl font-bold">{getSentimentPercentage(sentimentData.neutral)}%</p>
              <p className="text-gray-500 text-sm">of total</p>
            </div>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-gray-500 h-2 rounded-full" 
              style={{ width: `${getSentimentPercentage(sentimentData.neutral)}%` }}
            />
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-red-100 rounded-xl flex items-center justify-center">
                <TrendingDown className="w-6 h-6 text-red-600" />
              </div>
              <div>
                <p className="text-gray-600 text-sm font-medium">Negative Sentiment</p>
                <p className="text-2xl font-bold text-gray-900">{sentimentData.negative}</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-red-600 text-2xl font-bold">{getSentimentPercentage(sentimentData.negative)}%</p>
              <p className="text-gray-500 text-sm">of total</p>
            </div>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-red-500 h-2 rounded-full" 
              style={{ width: `${getSentimentPercentage(sentimentData.negative)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Sentiment Trends Chart */}
      <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <BarChart3 className="w-6 h-6 text-blue-600" />
            <h3 className="text-xl font-semibold text-gray-900">Sentiment Trends (Last 7 Days)</h3>
          </div>
          <div className="flex items-center space-x-1 text-sm text-gray-500">
            <Calendar className="w-4 h-4" />
            <span>Daily Analysis</span>
          </div>
        </div>

        {loading ? (
          <div className="h-80 flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
        ) : trendData.length > 0 ? (
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={trendData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => new Date(value).toLocaleDateString('en-IN', { 
                    month: 'short', 
                    day: 'numeric' 
                  })}
                />
                <YAxis />
                <Tooltip 
                  labelFormatter={(value) => `Date: ${new Date(value).toLocaleDateString('en-IN')}`}
                  formatter={(value: number, name: string) => [value, name.charAt(0).toUpperCase() + name.slice(1)]}
                />
                <Bar dataKey="negative" stackId="a" fill="#EF4444" name="negative" />
                <Bar dataKey="neutral" stackId="a" fill="#6B7280" name="neutral" />
                <Bar dataKey="positive" stackId="a" fill="#10B981" name="positive" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="h-80 flex items-center justify-center text-gray-500">
            <div className="text-center">
              <BarChart3 className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>No sentiment trend data available</p>
              <p className="text-sm">Data will appear as articles are analyzed</p>
            </div>
          </div>
        )}
      </div>

      {/* Sentiment Distribution Timeline */}
      <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
        <h3 className="text-xl font-semibold text-gray-900 mb-6">Sentiment Distribution Over Time</h3>
        
        {loading ? (
          <div className="h-64 flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
        ) : trendData.length > 0 ? (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => new Date(value).toLocaleDateString('en-IN', { 
                    month: 'short', 
                    day: 'numeric' 
                  })}
                />
                <YAxis />
                <Tooltip 
                  labelFormatter={(value) => `Date: ${new Date(value).toLocaleDateString('en-IN')}`}
                />
                <Line 
                  type="monotone" 
                  dataKey="positive" 
                  stroke="#10B981" 
                  strokeWidth={3}
                  dot={{ fill: '#10B981', strokeWidth: 2, r: 4 }}
                  name="Positive"
                />
                <Line 
                  type="monotone" 
                  dataKey="neutral" 
                  stroke="#6B7280" 
                  strokeWidth={3}
                  dot={{ fill: '#6B7280', strokeWidth: 2, r: 4 }}
                  name="Neutral"
                />
                <Line 
                  type="monotone" 
                  dataKey="negative" 
                  stroke="#EF4444" 
                  strokeWidth={3}
                  dot={{ fill: '#EF4444', strokeWidth: 2, r: 4 }}
                  name="Negative"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="h-64 flex items-center justify-center text-gray-500">
            <div className="text-center">
              <TrendingUp className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>No trend data available</p>
              <p className="text-sm">Timeline will populate as more articles are analyzed</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
