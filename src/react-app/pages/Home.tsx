import { useState } from 'react';
import Navigation from '../components/Navigation';
import Dashboard from '../components/Dashboard';
import NewsFeed from '../components/NewsFeed';
import SentimentAnalysis from '../components/SentimentAnalysis';
import LanguageInsights from '../components/LanguageInsights';

export default function Home() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'articles':
        return <NewsFeed />;
      case 'alerts':
        return (
          <div className="bg-white rounded-xl p-8 shadow-lg border border-gray-200 text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">PIB Alerts</h2>
            <p className="text-gray-600">Real-time government news alerts and notifications coming soon...</p>
          </div>
        );
      case 'officers':
        return (
          <div className="bg-white rounded-xl p-8 shadow-lg border border-gray-200 text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">PIB Officers</h2>
            <p className="text-gray-600">Officer management and notification system coming soon...</p>
          </div>
        );
      case 'sentiment':
        return <SentimentAnalysis />;
      case 'geographic':
        return (
          <div className="bg-white rounded-xl p-8 shadow-lg border border-gray-200 text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Geographic View</h2>
            <p className="text-gray-600">Regional news coverage mapping functionality coming soon...</p>
          </div>
        );
      case 'language':
        return <LanguageInsights />;
      case 'categories':
        return (
          <div className="bg-white rounded-xl p-8 shadow-lg border border-gray-200 text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Topic Categories</h2>
            <p className="text-gray-600">Government department categorization and analysis coming soon...</p>
          </div>
        );
      case 'filters':
        return (
          <div className="bg-white rounded-xl p-8 shadow-lg border border-gray-200 text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Advanced Filters</h2>
            <p className="text-gray-600">Advanced filtering and search capabilities coming soon...</p>
          </div>
        );
      case 'settings':
        return (
          <div className="bg-white rounded-xl p-8 shadow-lg border border-gray-200 text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Settings</h2>
            <p className="text-gray-600">System configuration and preferences coming soon...</p>
          </div>
        );
      default:
        return <Dashboard />;
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
