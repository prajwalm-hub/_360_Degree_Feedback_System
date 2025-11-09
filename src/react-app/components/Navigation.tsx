import { BarChart3, Newspaper, MessageSquare, Bell, TrendingUp, Map, Languages, FolderTree, Settings } from 'lucide-react';

interface NavigationProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export default function Navigation({ activeTab, onTabChange }: NavigationProps) {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: 'news', label: 'News Feed', icon: Newspaper },
    { id: 'assistant', label: 'AI Assistant', icon: MessageSquare },
    { id: 'alerts', label: 'PIB Alerts', icon: Bell },
    { id: 'sentiment', label: 'Sentiment Analysis', icon: TrendingUp },
    { id: 'geographic', label: 'Geographic View', icon: Map },
    { id: 'language', label: 'Language Insights', icon: Languages },
    { id: 'categories', label: 'Topic Categories', icon: FolderTree },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className="fixed left-0 top-0 h-screen w-64 bg-gray-900 text-white p-6 overflow-y-auto">
      {/* Logo */}
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-2">
          <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
            <Newspaper className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold">NewsScope</h1>
            <p className="text-xs text-gray-400">PIB Dashboard</p>
          </div>
        </div>
      </div>

      {/* Menu Items */}
      <nav className="space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                activeTab === item.id
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="text-sm font-medium">{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Status Indicator */}
      <div className="mt-8 pt-6 border-t border-gray-800">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-xs text-gray-400">Live Monitoring</span>
        </div>
      </div>
    </div>
  );
}
