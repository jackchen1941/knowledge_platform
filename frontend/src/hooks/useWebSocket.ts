import { useEffect, useRef, useState, useCallback } from 'react';
import { message } from 'antd';

interface WebSocketMessage {
  type: string;
  data?: any;
  timestamp?: string;
  message?: string;
}

interface WebSocketHookOptions {
  onMessage?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

interface WebSocketHookReturn {
  isConnected: boolean;
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error';
  sendMessage: (message: any) => void;
  subscribe: (room: string) => void;
  unsubscribe: (room: string) => void;
  reconnect: () => void;
  disconnect: () => void;
  lastMessage: WebSocketMessage | null;
  connectionStats: any;
}

export const useWebSocket = (
  userId: string | null,
  token: string | null,
  options: WebSocketHookOptions = {}
): WebSocketHookReturn => {
  const {
    onMessage,
    onConnect,
    onDisconnect,
    onError,
    reconnectInterval = 3000,
    maxReconnectAttempts = 5
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [connectionStats, setConnectionStats] = useState<any>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const getWebSocketUrl = useCallback(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    return `${protocol}//${host}/api/v1/ws/${userId}?token=${token}`;
  }, [userId, token]);

  const sendMessage = useCallback((messageData: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(messageData));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  const subscribe = useCallback((room: string) => {
    sendMessage({ type: 'subscribe', room });
  }, [sendMessage]);

  const unsubscribe = useCallback((room: string) => {
    sendMessage({ type: 'unsubscribe', room });
  }, [sendMessage]);

  const startPingInterval = useCallback(() => {
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
    }
    
    pingIntervalRef.current = setInterval(() => {
      sendMessage({ type: 'ping' });
    }, 30000); // Ping every 30 seconds
  }, [sendMessage]);

  const stopPingInterval = useCallback(() => {
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }
  }, []);

  const connect = useCallback(() => {
    if (!userId || !token) {
      console.warn('Cannot connect WebSocket: missing userId or token');
      return;
    }

    if (wsRef.current && wsRef.current.readyState === WebSocket.CONNECTING) {
      return; // Already connecting
    }

    setConnectionStatus('connecting');

    try {
      const wsUrl = getWebSocketUrl();
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setConnectionStatus('connected');
        reconnectAttemptsRef.current = 0;
        
        // Start ping interval
        startPingInterval();
        
        // Get initial stats
        sendMessage({ type: 'get_stats' });
        
        onConnect?.();
      };

      wsRef.current.onmessage = (event) => {
        try {
          const messageData: WebSocketMessage = JSON.parse(event.data);
          setLastMessage(messageData);

          // Handle specific message types
          switch (messageData.type) {
            case 'notification':
              // Show notification in UI
              if (messageData.data) {
                const notificationData = messageData.data;
                const notificationType = notificationData.notification_type || 'info';
                
                // Map notification types to antd message types
                const messageType = notificationType === 'error' ? 'error' :
                                  notificationType === 'warning' ? 'warning' :
                                  notificationType === 'success' ? 'success' : 'info';
                
                message[messageType](notificationData.title);
              }
              break;
              
            case 'sync_update':
              // Handle sync updates
              console.log('Sync update received:', messageData.data);
              break;
              
            case 'system_message':
              // Handle system messages
              if (messageData.data?.message) {
                message.info(messageData.data.message);
              }
              break;
              
            case 'stats':
              // Update connection stats
              setConnectionStats(messageData.data);
              break;
              
            case 'pong':
              // Handle ping response
              console.log('WebSocket ping response received');
              break;
              
            case 'connection_established':
              console.log('WebSocket connection established');
              break;
              
            case 'error':
              console.error('WebSocket error message:', messageData.message);
              break;
              
            default:
              console.log('Unknown WebSocket message type:', messageData.type);
          }

          onMessage?.(messageData);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      wsRef.current.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setIsConnected(false);
        setConnectionStatus('disconnected');
        stopPingInterval();
        
        onDisconnect?.();

        // Attempt to reconnect if not a normal closure
        if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          console.log(`Attempting to reconnect (${reconnectAttemptsRef.current}/${maxReconnectAttempts})...`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('error');
        onError?.(error);
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setConnectionStatus('error');
    }
  }, [userId, token, getWebSocketUrl, onConnect, onDisconnect, onError, onMessage, maxReconnectAttempts, reconnectInterval, sendMessage, startPingInterval, stopPingInterval]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    stopPingInterval();
    
    if (wsRef.current) {
      wsRef.current.close(1000, 'Manual disconnect');
      wsRef.current = null;
    }
    
    setIsConnected(false);
    setConnectionStatus('disconnected');
  }, [stopPingInterval]);

  const reconnect = useCallback(() => {
    disconnect();
    setTimeout(() => {
      reconnectAttemptsRef.current = 0;
      connect();
    }, 1000);
  }, [disconnect, connect]);

  // Auto-connect when userId and token are available
  useEffect(() => {
    if (userId && token) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [userId, token, connect, disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    isConnected,
    connectionStatus,
    sendMessage,
    subscribe,
    unsubscribe,
    reconnect,
    disconnect,
    lastMessage,
    connectionStats
  };
};