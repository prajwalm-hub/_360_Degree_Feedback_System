import { useState } from 'react';
import Navigation from '../components/Navigation';
import Dashboard from '../components/Dashboard';
import NewsFeed from '../components/NewsFeed';
import SentimentAnalysis from '../components/SentimentAnalysis';
import LanguageInsights from '../components/LanguageInsights';

export default function Home() {
  const [activeTab, setActiveTab] = useState('sentiment');

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'news':
        return <NewsFeed />;
      case 'assistant':
        return (
          <div className="bg-white rounded-xl p-8 shadow-lg border border-gray-200 text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">AI Assistant</h2>
            <p className="text-gray-600">AI-powered news analysis assistant coming soon...</p>
          </div>
        );
      case 'alerts':
        return (
          <div className="bg-white rounded-xl p-8 shadow-lg border border-gray-200 text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">PIB Alerts</h2>
            <p className="text-gray-600">Real-time government news alerts coming soon...</p>
          </div>
        );
      case 'sentiment':
        return <SentimentAnalysis />;
      case 'geographic':
        return (
          <div className="bg-white rounded-xl p-8 shadow-lg border border-gray-200 text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Geographic View</h2>
            <p className="text-gray-600">Regional news coverage mapping coming soon...</p>
          </div>
        );
      case 'language':
        return <LanguageInsights />;
      case 'categories':
        return (
          <div className="bg-white rounded-xl p-8 shadow-lg border border-gray-200 text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Topic Categories</h2>
            <p className="text-gray-600">Topic categorization coming soon...</p>
          </div>
        );
      case 'settings':
        return (
          <div className="bg-white rounded-xl p-8 shadow-lg border border-gray-200 text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Settings</h2>
            <p className="text-gray-600">System settings coming soon...</p>
          </div>
        );
      default:
        return <SentimentAnalysis />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100">
      <Navigation activeTab={activeTab} onTabChange={setActiveTab} />
      
      <div className="lg:ml-64 p-6">
        <div className="max-w-7xl mx-auto">
          {renderContent()}
        </div>
      </div>
    </div>
  );
}
