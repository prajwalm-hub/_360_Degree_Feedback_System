import { useEffect, useState } from 'react';
import { 
  Brain, 
  Cpu, 
  Database, 
  Rss,
  Activity,
  CheckCircle,
  AlertCircle,
  Clock,
  TrendingUp
} from 'lucide-react';

interface ProcessingStats {
  job_statistics: Array<{
    status: string;
    count: number;
  }>;
  active_sources: number;
  timestamp: string;
}

interface JobStatus {
  pending: number;
  processing: number;
  completed: number;
  failed: number;
}

export default function AIProcessingStatus() {
  const [stats, setStats] = useState<ProcessingStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<string>('');

  useEffect(() => {
    fetchProcessingStatus();
    const interval = setInterval(fetchProcessingStatus, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchProcessingStatus = async () => {
    try {
      const response = await fetch('/api/python/status');
      const data = await response.json();
      if (data.success) {
        setStats(data.data);
        setLastUpdate(new Date().toLocaleTimeString());
      }
    } catch (error) {
      console.error('Failed to fetch processing status:', error);
    } finally {
      setLoading(false);
    }
  };

  const triggerNewsCollection = async () => {
    try {
      const response = await fetch('/api/python/collect-news', { method: 'POST' });
      const data = await response.json();
      if (data.success) {
        // Refresh status after triggering
        setTimeout(fetchProcessingStatus, 2000);
      }
    } catch (error) {
      console.error('Failed to trigger news collection:', error);
    }
  };

  const triggerProcessing = async () => {
    try {
      const response = await fetch('/api/python/process-articles', { method: 'POST' });
      const data = await response.json();
      if (data.success) {
        // Refresh status after triggering
        setTimeout(fetchProcessingStatus, 2000);
      }
    } catch (error) {
      console.error('Failed to trigger processing:', error);
    }
  };

  const triggerCompleteCycle = async () => {
    try {
      const response = await fetch('/api/python/run-cycle', { method: 'POST' });
      const data = await response.json();
      if (data.success) {
        // Refresh status after triggering
        setTimeout(fetchProcessingStatus, 5000);
      }
    } catch (error) {
      console.error('Failed to trigger complete cycle:', error);
    }
  };

  const getJobStatus = (): JobStatus => {
    if (!stats) return { pending: 0, processing: 0, completed: 0, failed: 0 };
    
    const jobStatus: JobStatus = { pending: 0, processing: 0, completed: 0, failed: 0 };
    
    stats.job_statistics.forEach(job => {
      jobStatus[job.status as keyof JobStatus] = job.count;
    });
    
    return jobStatus;
  };

  const jobStatus = getJobStatus();
  const totalJobs = Object.values(jobStatus).reduce((sum, count) => sum + count, 0);

  if (loading) {
    return (
      <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center">
            <Brain className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">AI/ML Processing Status</h3>
            <p className="text-sm text-gray-500">Real-time news analysis pipeline</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-xs text-gray-500">Last updated</p>
          <p className="text-sm font-medium text-gray-700">{lastUpdate}</p>
        </div>
      </div>

      {/* Processing Statistics */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
          <div className="flex items-center space-x-2">
            <Clock className="w-5 h-5 text-blue-600" />
            <div>
              <p className="text-sm text-blue-600 font-medium">Pending</p>
              <p className="text-2xl font-bold text-blue-700">{jobStatus.pending}</p>
            </div>
          </div>
        </div>

        <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
          <div className="flex items-center space-x-2">
            <Cpu className="w-5 h-5 text-yellow-600" />
            <div>
              <p className="text-sm text-yellow-600 font-medium">Processing</p>
              <p className="text-2xl font-bold text-yellow-700">{jobStatus.processing}</p>
            </div>
          </div>
        </div>

        <div className="bg-green-50 rounded-lg p-4 border border-green-200">
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <div>
              <p className="text-sm text-green-600 font-medium">Completed</p>
              <p className="text-2xl font-bold text-green-700">{jobStatus.completed}</p>
            </div>
          </div>
        </div>

        <div className="bg-red-50 rounded-lg p-4 border border-red-200">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <div>
              <p className="text-sm text-red-600 font-medium">Failed</p>
              <p className="text-2xl font-bold text-red-700">{jobStatus.failed}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Active Sources */}
      <div className="flex items-center justify-between mb-6 p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center space-x-3">
          <Rss className="w-5 h-5 text-gray-600" />
          <div>
            <p className="text-sm font-medium text-gray-900">Active RSS Sources</p>
            <p className="text-xs text-gray-500">Monitoring regional news feeds</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-gray-900">{stats?.active_sources || 0}</p>
          <p className="text-xs text-gray-500">Sources</p>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <button
          onClick={triggerNewsCollection}
          className="flex items-center justify-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          <Database className="w-4 h-4" />
          <span className="text-sm font-medium">Collect News</span>
        </button>

        <button
          onClick={triggerProcessing}
          className="flex items-center justify-center space-x-2 px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors"
        >
          <Brain className="w-4 h-4" />
          <span className="text-sm font-medium">Process Articles</span>
        </button>

        <button
          onClick={triggerCompleteCycle}
          className="flex items-center justify-center space-x-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
        >
          <Activity className="w-4 h-4" />
          <span className="text-sm font-medium">Run Full Cycle</span>
        </button>
      </div>

      {/* AI/ML Features List */}
      <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
        <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
          <TrendingUp className="w-4 h-4 mr-2" />
          AI/ML Capabilities
        </h4>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span className="text-gray-700">Sentiment Analysis</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <span className="text-gray-700">Language Detection</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
            <span className="text-gray-700">Content Translation</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
            <span className="text-gray-700">Auto-Categorization</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-red-500 rounded-full"></div>
            <span className="text-gray-700">Entity Extraction</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
            <span className="text-gray-700">Alert Generation</span>
          </div>
        </div>
      </div>
    </div>
  );
}
