import { useEffect, useCallback, useRef } from 'react';
import { API_CONFIG } from '../config/api';

export const useWebSocket = (debateId, clientId, onNewMessage, onJurorResponse) => {
  const wsRef = useRef(null);

  const connectWebSocket = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    // Convert http(s):// to ws(s)://
    const wsUrl = API_CONFIG.BACKEND_URL.replace(/^http/, 'ws');
    const ws = new WebSocket(`${wsUrl}/ws/${debateId}/${clientId}`);

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'new_message':
          onNewMessage(data.data);
          break;
        case 'juror_response':
          onJurorResponse(data.data);
          break;
        default:
          console.log('Unknown message type:', data.type);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      wsRef.current = null;
      // Try to reconnect after a delay
      setTimeout(connectWebSocket, 3000);
    };

    wsRef.current = ws;
  }, [debateId, clientId, onNewMessage, onJurorResponse]);

  const disconnectWebSocket = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  useEffect(() => {
    if (!debateId || !clientId) return;
    connectWebSocket();
    return () => {
      disconnectWebSocket();
    };
  }, [debateId, clientId, connectWebSocket, disconnectWebSocket]);

  return {
    connectWebSocket,
    disconnectWebSocket,
    isConnected: wsRef.current?.readyState === WebSocket.OPEN
  };
};