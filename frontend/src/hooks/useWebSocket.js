import { useEffect, useCallback } from 'react';
import { API_CONFIG } from '../config/api';

export const useWebSocket = (debateId, clientId, onNewMessage, onJurorResponse) => {
  const connectWebSocket = useCallback(() => {
    // Convert http(s):// to ws(s)://
    const wsUrl = API_CONFIG.BACKEND_URL.replace(/^http/, 'ws');
    
    // Ensure debateId is a string
    const debateIdStr = debateId?.toString() || '';
    const clientIdStr = clientId?.toString() || '';
    
    console.log('Attempting WebSocket connection to:', `${wsUrl}/ws/${debateIdStr}/${clientIdStr}`);

    let reconnectAttempts = 0;
    const MAX_RECONNECT_ATTEMPTS = 5;
    let pingInterval;
    
    const ws = new WebSocket(`${wsUrl}/ws/${debateIdStr}/${clientIdStr}`);

    // Set a timeout for the initial connection
    const connectionTimeout = setTimeout(() => {
      if (ws.readyState !== WebSocket.OPEN) {
        console.error('WebSocket connection timeout');
        ws.close();
      }
    }, 10000); // 10 seconds timeout

    ws.onopen = () => {
      console.log('WebSocket connected successfully');
      clearTimeout(connectionTimeout);
      reconnectAttempts = 0;

      // Setup ping interval to keep connection alive
      pingInterval = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'ping' }));
        }
      }, 30000); // Send ping every 30 seconds
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('Received WebSocket message:', data);
        
        if (data.type === 'pong') {
          console.log('Received pong from server');
          return;
        }
        
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
      } catch (error) {
        console.error('Error processing WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      clearTimeout(connectionTimeout);
      clearInterval(pingInterval);
      
      // Check if the error is due to mixed content
      const isMixedContent = window.location.protocol === 'https:' && wsUrl.startsWith('ws://');
      
      console.error('WebSocket error details:', {
        readyState: ws.readyState,
        url: ws.url,
        protocol: ws.protocol,
        error: error,
        debateId: debateIdStr,
        clientId: clientIdStr,
        isMixedContent,
        browserProtocol: window.location.protocol,
        wsProtocol: wsUrl.split(':')[0]
      });
    };

    ws.onclose = (event) => {
      clearTimeout(connectionTimeout);
      clearInterval(pingInterval);
      
      console.log('WebSocket closed with code:', event.code, 'reason:', event.reason || 'No reason provided');
      console.log('WebSocket close event details:', {
        wasClean: event.wasClean,
        code: event.code,
        reason: event.reason || 'No reason provided'
      });
      
      // Implement exponential backoff for reconnection
      if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        const timeout = Math.min(1000 * Math.pow(2, reconnectAttempts), 10000);
        console.log(`Attempting to reconnect in ${timeout}ms (attempt ${reconnectAttempts + 1}/${MAX_RECONNECT_ATTEMPTS})`);
        setTimeout(() => {
          reconnectAttempts++;
          connectWebSocket();
        }, timeout);
      } else {
        console.error('Max reconnection attempts reached. Please refresh the page to try again.');
      }
    };

    return () => {
      clearTimeout(connectionTimeout);
      clearInterval(pingInterval);
      if (ws.readyState === WebSocket.OPEN) {
        ws.close(1000, 'Component unmounting');
      }
    };
  }, [debateId, clientId, onNewMessage, onJurorResponse]);

  useEffect(() => {
    if (!debateId || !clientId) {
      console.log('Missing required WebSocket parameters:', { debateId, clientId });
      return;
    }

    console.log('Initializing WebSocket connection with:', { debateId, clientId });
    const cleanup = connectWebSocket();

    return () => {
      console.log('Cleaning up WebSocket connection');
      cleanup();
    };
  }, [debateId, clientId, connectWebSocket]);
}; 