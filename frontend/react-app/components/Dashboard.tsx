import { useEffect, useState } from 'react';
import {
  TrendingUp,
  Globe,
  AlertCircle,
  Newspaper,
  BarChart3
} from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';
import type { DashboardStats } from '@/shared/types';

const SENTIMENT_COLORS = {
  positive: '#10B981',
  neutral: '#6B7280', 
  negative: '#EF4444'
};

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'all' | 'government'>('all');

  useEffect(() => {
    fetchDashboardStats();
  }, [viewMode]);

  const fetchDashboardStats = async () => {
    try {
      const endpoint = viewMode === 'government' ? '/api/government/dashboard/stats/' : '/api/dashboard/stats';
      const response = await fetch(endpoint);
      const data = await response.json();
      if (data.success || !data.success) { // Handle both response formats
        setStats(data.data || data);
      }
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const sentimentData = stats ? [
    { name: 'Positive', value: stats.sentiment_distribution.positive, color: SENTIMENT_COLORS.positive },
    { name: 'Neutral', value: stats.sentiment_distribution.neutral, color: SENTIMENT_COLORS.neutral },
    { name: 'Negative', value: stats.sentiment_distribution.negative, color: SENTIMENT_COLORS.negative }
  ] : [];

  const totalSentiment = sentimentData.reduce((sum, item) => sum + item.value, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-700 rounded-2xl p-8 text-white">
        <h1 className="text-3xl font-bold mb-2">Government News Monitor</h1>
        <p className="text-blue-100">Real-time AI-powered sentiment analysis across regional media</p>
        <div className="mt-4 flex space-x-4">
          <button
            onClick={() => setViewMode('all')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              viewMode === 'all' ? 'bg-white text-blue-600' : 'bg-blue-500 text-white hover:bg-blue-400'
            }`}
          >
            All News
          </button>
          <button
            onClick={() => setViewMode('government')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              viewMode === 'government' ? 'bg-white text-blue-600' : 'bg-blue-500 text-white hover:bg-blue-400'
            }`}
          >
            Government News
          </button>
        </div>
      </div>



      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Total Articles</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.total_articles || 0}</p>
            </div>
            <div className="w-12 h-12 bg-blue-500 rounded-xl flex items-center justify-center">
              <Newspaper className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Active Sources</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.total_sources || 0}</p>
            </div>
            <div className="w-12 h-12 bg-green-500 rounded-xl flex items-center justify-center">
              <Globe className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Languages</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.total_languages || 0}</p>
            </div>
            <div className="w-12 h-12 bg-purple-500 rounded-xl flex items-center justify-center">
              <BarChart3 className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Active Alerts</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.recent_alerts.length || 0}</p>
            </div>
            <div className="w-12 h-12 bg-red-500 rounded-xl flex items-center justify-center">
              <AlertCircle className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sentiment Distribution */}
        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Sentiment Distribution</h3>
          {totalSentiment > 0 ? (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={sentimentData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {sentimentData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-500">
              No sentiment data available
            </div>
          )}
          
          <div className="mt-4 space-y-2">
            {sentimentData.map((item) => (
              <div key={item.name} className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div 
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-sm text-gray-600">{item.name}</span>
                </div>
                <span className="text-sm font-medium text-gray-900">{item.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Regional Coverage */}
        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Regional Coverage</h3>
          {stats?.regional_coverage && stats.regional_coverage.length > 0 ? (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stats.regional_coverage}>
                  <XAxis dataKey="region" tick={{ fontSize: 12 }} />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-500">
              No regional data available
            </div>
          )}
        </div>
      </div>

      {/* Trending Topics & Recent Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Trending Topics */}
        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
          <div className="flex items-center space-x-2 mb-4">
            <TrendingUp className="w-5 h-5 text-green-500" />
            <h3 className="text-lg font-semibold text-gray-900">Trending Topics</h3>
          </div>
          <div className="space-y-3">
            {stats?.trending_topics && stats.trending_topics.length > 0 ? (
              stats.trending_topics.map((topic: string, index: number) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-gray-900 font-medium">{topic}</span>
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-center py-8">No trending topics available</p>
            )}
          </div>
        </div>

        {/* Recent Alerts */}
        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
          <div className="flex items-center space-x-2 mb-4">
            <AlertCircle className="w-5 h-5 text-red-500" />
            <h3 className="text-lg font-semibold text-gray-900">Recent Alerts</h3>
          </div>
          <div className="space-y-3">
            {stats?.recent_alerts && stats.recent_alerts.length > 0 ? (
              stats.recent_alerts.map((alert: any) => (
                <div key={alert.id} className="p-3 bg-red-50 border border-red-200 rounded-lg">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-medium text-red-900">{alert.title}</p>
                      <p className="text-sm text-red-700 mt-1">{alert.content}</p>
                    </div>
                    <span className={`
                      px-2 py-1 rounded-full text-xs font-medium
                      ${alert.severity === 'critical' ? 'bg-red-500 text-white' : 
                        alert.severity === 'high' ? 'bg-orange-500 text-white' :
                        alert.severity === 'medium' ? 'bg-yellow-500 text-white' : 'bg-blue-500 text-white'}
                    `}>
                      {alert.severity}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-center py-8">No active alerts</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
