import { useEffect, useCallback, useRef } from 'react';
import { API_CONFIG } from '../config/api';

export const useWebSocket = (debateId, clientId, onNewMessage, onJurorResponse, onJudgeMessage) => {
  const wsRef = useRef(null);

  const connectWebSocket = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    // Convert http(s):// to ws(s)://
    const wsUrl = API_CONFIG.BACKEND_URL.replace(/^http/, 'ws').replace(/^https/, 'wss');
    console.log('Connecting to WebSocket URL:', wsUrl);
    const ws = new WebSocket(`${wsUrl}/ws/${debateId}/${clientId}`);

    ws.onopen = () => {
      console.log('WebSocket connected successfully');
      // 连接成功后立即请求最新的 juror 响应
      if (onJurorResponse) {
        fetch(`${API_CONFIG.BACKEND_URL}/juror_results/${debateId}`)
          .then(response => response.json())
          .then(data => {
            console.log('Fetched latest juror results:', data);
            if (data && data.length > 0) {
              const latestResponse = data[data.length - 1];
              onJurorResponse({
                message_id: latestResponse.message_id,
                responses: latestResponse.responses
              });
            }
          })
          .catch(error => console.error('Error fetching juror results:', error));
      }
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('WebSocket received message:', data);
      
      switch (data.type) {
        case 'new_message':
          // Check if it's a judge agent message and has a valid ID
          if (data.data?.username === "Judge Agent" && data.data?.id) {
            console.log('Received judge message:', data.data);
            onJudgeMessage(data.data);
          } else {
            console.log('Received regular user message:', data.data);
          }
          onNewMessage(data.data);
          break;
        case 'juror_response':
          console.log('Received juror response for message:', data.data.message_id);
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
  }, [debateId, clientId, onNewMessage, onJurorResponse, onJudgeMessage]);

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