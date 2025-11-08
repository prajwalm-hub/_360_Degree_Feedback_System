/**
 * React hook for WebSocket connection to real-time news feed
 */

import { useEffect, useRef, useState, useCallback } from 'react';

export interface NewsArticle {
  title: string;
  content: string;
  url: string;
  source: string;
  language: string;
  category: string;
  region: string;
  publish_date: string;
  collected_date: string;
  sentiment?: {
    sentiment: string;
    confidence: number;
    scores: Record<string, number>;
  };
  summary?: string;
  entities?: Array<{
    entity: string;
    label: string;
    confidence: number;
    start: number;
    end: number;
  }>;
  is_government_related?: boolean;
  government_confidence?: number;
  keywords?: string[];
  ai_processed?: boolean;
  ai_confidence_score?: number;
}

export interface WebSocketMessage {
  type: 'new_article' | 'welcome' | 'subscribed' | 'pong' | 'stats';
  data?: NewsArticle | any;
  message?: string;
  timestamp: number;
  topics?: string[];
}

export interface SystemStats {
  connected_clients: number;
  uptime: number;
  server_version: string;
}

export const useWebSocket = (url: string = 'ws://localhost:8765') => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [newsArticles, setNewsArticles] = useState<NewsArticle[]>([]);
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout>();
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;
  const reconnectDelay = 3000;

  const connect = useCallback(() => {
    try {
      ws.current = new WebSocket(url);

      ws.current.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setError(null);
        reconnectAttempts.current = 0;
      };

      ws.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setLastMessage(message);

          switch (message.type) {
            case 'new_article':
              if (message.data) {
                setNewsArticles(prev => [message.data as NewsArticle, ...prev.slice(0, 99)]); // Keep last 100
              }
              break;
            case 'stats':
              if (message.data) {
                setSystemStats(message.data as SystemStats);
              }
              break;
            case 'welcome':
              console.log('WebSocket welcome:', message.message);
              break;
            case 'subscribed':
              console.log('Subscribed to topics:', message.topics);
              break;
            default:
              console.log('Received message:', message);
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };

      ws.current.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setIsConnected(false);

        // Attempt to reconnect if not a normal closure
        if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
          reconnectAttempts.current++;
          console.log(`Attempting to reconnect (${reconnectAttempts.current}/${maxReconnectAttempts})...`);

          reconnectTimeout.current = setTimeout(() => {
            connect();
          }, reconnectDelay);
        } else if (reconnectAttempts.current >= maxReconnectAttempts) {
          setError('Failed to reconnect after maximum attempts');
        }
      };

      ws.current.onerror = (event) => {
        console.error('WebSocket error:', event);
        setError('WebSocket connection error');
      };

    } catch (err) {
      console.error('Failed to create WebSocket connection:', err);
      setError('Failed to create WebSocket connection');
    }
  }, [url, maxReconnectAttempts, reconnectDelay]);

  const disconnect = useCallback(() => {
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
    }

    if (ws.current) {
      ws.current.close(1000, 'Client disconnecting');
      ws.current = null;
    }

    setIsConnected(false);
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  const subscribeToTopics = useCallback((topics: string[]) => {
    sendMessage({
      type: 'subscribe',
      topics: topics
    });
  }, [sendMessage]);

  const requestStats = useCallback(() => {
    sendMessage({
      type: 'get_stats'
    });
  }, [sendMessage]);

  const sendPing = useCallback(() => {
    sendMessage({
      type: 'ping'
    });
  }, [sendMessage]);

  // Auto-connect on mount
  useEffect(() => {
    connect();

    // Cleanup on unmount
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  // Auto-ping every 30 seconds to keep connection alive
  useEffect(() => {
    if (isConnected) {
      const pingInterval = setInterval(() => {
        sendPing();
      }, 30000);

      return () => clearInterval(pingInterval);
    }
  }, [isConnected, sendPing]);

  return {
    isConnected,
    lastMessage,
    newsArticles,
    systemStats,
    error,
    connect,
    disconnect,
    sendMessage,
    subscribeToTopics,
    requestStats,
    sendPing
  };
};

export default useWebSocket;
