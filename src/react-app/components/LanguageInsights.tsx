import { useEffect, useState } from 'react';
import { 
  Languages, 
  Globe, 
  BarChart3,
  RefreshCw,
  TrendingUp
} from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

interface LanguageData {
  language: string;
  name: string;
  count: number;
  region: string;
  sentiment_avg: number;
}

interface RegionData {
  region: string;
  languages: number;
  articles: number;
  dominant_language: string;
}

const LANGUAGE_NAMES: { [key: string]: string } = {
  'en': 'English',
  'hi': 'Hindi',
  'ta': 'Tamil',
  'te': 'Telugu', 
  'bn': 'Bengali',
  'gu': 'Gujarati',
  'kn': 'Kannada',
  'ml': 'Malayalam',
  'mr': 'Marathi',
  'pa': 'Punjabi',
  'ur': 'Urdu',
  'or': 'Odia',
  'as': 'Assamese'
};

const REGION_COLORS = [
  '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4',
  '#84CC16', '#F97316', '#EC4899', '#6366F1', '#14B8A6', '#F59E0B'
];

export default function LanguageInsights() {
  const [languageData, setLanguageData] = useState<LanguageData[]>([]);
  const [regionData, setRegionData] = useState<RegionData[]>([]);
  const [loading, setLoading] = useState(true);
  const [totalArticles, setTotalArticles] = useState(0);

  useEffect(() => {
    fetchLanguageData();
  }, []);

  const fetchLanguageData = async () => {
    try {
      setLoading(true);
      
      // Get language distribution from articles
      const response = await fetch('/api/articles?limit=1000');
      const data = await response.json();
      
      if (data.success) {
        processLanguageData(data.data || []);
      }
    } catch (error) {
      console.error('Failed to fetch language data:', error);
    } finally {
      setLoading(false);
    }
  };

  const processLanguageData = (articles: any[]) => {
    setTotalArticles(articles.length);
    
    // Process language statistics
    const langStats: { [key: string]: { count: number; regions: Set<string>; sentiments: number[] } } = {};
    const regionStats: { [key: string]: { languages: Set<string>; articles: number; langCounts: { [key: string]: number } } } = {};
    
    articles.forEach((article) => {
      const lang = article.language || 'unknown';
      const region = article.region || 'Unknown';
      const sentiment = article.sentiment_score || 0;
      
      // Language stats
      if (!langStats[lang]) {
        langStats[lang] = { count: 0, regions: new Set(), sentiments: [] };
      }
      langStats[lang].count++;
      langStats[lang].regions.add(region);
      langStats[lang].sentiments.push(sentiment);
      
      // Region stats
      if (!regionStats[region]) {
        regionStats[region] = { languages: new Set(), articles: 0, langCounts: {} };
      }
      regionStats[region].languages.add(lang);
      regionStats[region].articles++;
      regionStats[region].langCounts[lang] = (regionStats[region].langCounts[lang] || 0) + 1;
    });
    
    // Convert to arrays for visualization
    const languageArray: LanguageData[] = Object.entries(langStats).map(([lang, stats]) => ({
      language: lang,
      name: LANGUAGE_NAMES[lang] || lang.toUpperCase(),
      count: stats.count,
      region: Array.from(stats.regions).join(', '),
      sentiment_avg: stats.sentiments.reduce((sum, s) => sum + s, 0) / stats.sentiments.length || 0
    })).sort((a, b) => b.count - a.count);
    
    const regionArray: RegionData[] = Object.entries(regionStats).map(([region, stats]) => {
      const dominantLang = Object.entries(stats.langCounts).reduce((a, b) => 
        stats.langCounts[a[0]] > stats.langCounts[b[0]] ? a : b
      )[0];
      
      return {
        region,
        languages: stats.languages.size,
        articles: stats.articles,
        dominant_language: LANGUAGE_NAMES[dominantLang] || dominantLang.toUpperCase()
      };
    }).sort((a, b) => b.articles - a.articles);
    
    setLanguageData(languageArray);
    setRegionData(regionArray);
  };

  const getLanguagePercentage = (count: number) => {
    return totalArticles > 0 ? Math.round((count / totalArticles) * 100) : 0;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-700 rounded-2xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Language Insights</h1>
            <p className="text-purple-100">Multilingual news coverage analysis across Indian regions</p>
          </div>
          <button
            onClick={fetchLanguageData}
            disabled={loading}
            className="flex items-center space-x-2 px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Language Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
              <Languages className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p className="text-gray-600 text-sm font-medium">Total Languages</p>
              <p className="text-3xl font-bold text-gray-900">{languageData.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
              <Globe className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-gray-600 text-sm font-medium">Regions Covered</p>
              <p className="text-3xl font-bold text-gray-900">{regionData.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
              <BarChart3 className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <p className="text-gray-600 text-sm font-medium">Total Articles</p>
              <p className="text-3xl font-bold text-gray-900">{totalArticles}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-orange-600" />
            </div>
            <div>
              <p className="text-gray-600 text-sm font-medium">Most Used</p>
              <p className="text-xl font-bold text-gray-900">{languageData[0]?.name || 'N/A'}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Language Distribution Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Language Distribution Pie Chart */}
        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
          <h3 className="text-xl font-semibold text-gray-900 mb-6">Language Distribution</h3>
          
          {loading ? (
            <div className="h-80 flex items-center justify-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
            </div>
          ) : languageData.length > 0 ? (
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={languageData.slice(0, 8).map(lang => ({ name: lang.name, count: lang.count }))} // Show top 8 languages
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={120}
                    paddingAngle={2}
                    dataKey="count"
                    label={({ name, value }) => `${name}: ${value}`}
                  >
                    {languageData.slice(0, 8).map((_, index) => (
                      <Cell key={`cell-${index}`} fill={REGION_COLORS[index % REGION_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => [value, 'Articles']} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-80 flex items-center justify-center text-gray-500">
              <div className="text-center">
                <Languages className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>No language data available</p>
              </div>
            </div>
          )}
        </div>

        {/* Regional Coverage Bar Chart */}
        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
          <h3 className="text-xl font-semibold text-gray-900 mb-6">Regional Coverage</h3>
          
          {loading ? (
            <div className="h-80 flex items-center justify-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
            </div>
          ) : regionData.length > 0 ? (
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={regionData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="region" tick={{ fontSize: 12 }} angle={-45} textAnchor="end" height={80} />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="articles" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-80 flex items-center justify-center text-gray-500">
              <div className="text-center">
                <Globe className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>No regional data available</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Detailed Language Statistics */}
      <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
        <h3 className="text-xl font-semibold text-gray-900 mb-6">Detailed Language Statistics</h3>
        
        {loading ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
          </div>
        ) : languageData.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">Language</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">Articles</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">Percentage</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">Regions</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">Avg Sentiment</th>
                </tr>
              </thead>
              <tbody>
                {languageData.map((lang, index) => (
                  <tr key={lang.language} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-3">
                        <div 
                          className="w-4 h-4 rounded-full"
                          style={{ backgroundColor: REGION_COLORS[index % REGION_COLORS.length] }}
                        />
                        <span className="font-medium text-gray-900">{lang.name}</span>
                        <span className="text-gray-500 text-sm">({lang.language})</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 font-semibold text-gray-900">{lang.count}</td>
                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-2">
                        <div className="w-16 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-purple-500 h-2 rounded-full" 
                            style={{ width: `${getLanguagePercentage(lang.count)}%` }}
                          />
                        </div>
                        <span className="text-gray-600 text-sm">{getLanguagePercentage(lang.count)}%</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-gray-600 text-sm">{lang.region}</td>
                    <td className="py-3 px-4">
                      <span className={`
                        px-2 py-1 rounded-full text-xs font-medium
                        ${lang.sentiment_avg > 0.2 ? 'bg-green-100 text-green-800' :
                          lang.sentiment_avg < -0.2 ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-800'}
                      `}>
                        {lang.sentiment_avg.toFixed(2)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <Languages className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>No language statistics available</p>
            <p className="text-sm">Data will appear as articles are collected and analyzed</p>
          </div>
        )}
      </div>
    </div>
  );
}
