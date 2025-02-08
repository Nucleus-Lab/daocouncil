import { useEffect, useCallback } from 'react';
import { API_CONFIG } from '../config/api';

export const useWebSocket = (debateId, clientId, onNewMessage, onJurorResponse, onJudgeMessage) => {
  const connectWebSocket = useCallback(() => {
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
          // Check if it's a judge agent message and has a valid ID
          if (data.data?.username === "Judge Agent" && data.data?.id) {
            onJudgeMessage(data.data);
          }
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
      // Try to reconnect after a delay
      setTimeout(connectWebSocket, 3000);
    };

    return ws;
  }, [debateId, clientId, onNewMessage, onJurorResponse, onJudgeMessage]);

  useEffect(() => {
    if (!debateId || !clientId) return;

    const ws = connectWebSocket();

    return () => {
      ws.close();
    };
  }, [debateId, clientId, connectWebSocket]);
}; 