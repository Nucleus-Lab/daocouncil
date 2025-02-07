import { useEffect, useCallback } from 'react';

export const useWebSocket = (debateId, clientId, onNewMessage, onJurorResponse) => {
  const connectWebSocket = useCallback(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${debateId}/${clientId}`);

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
      // Try to reconnect after a delay
      setTimeout(connectWebSocket, 3000);
    };

    return ws;
  }, [debateId, clientId, onNewMessage, onJurorResponse]);

  useEffect(() => {
    if (!debateId || !clientId) return;

    const ws = connectWebSocket();

    return () => {
      ws.close();
    };
  }, [debateId, clientId, connectWebSocket]);
}; 