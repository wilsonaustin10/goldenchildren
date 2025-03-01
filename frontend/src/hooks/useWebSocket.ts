'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { API_BASE_URL } from '@/api/base';

// Replace http:// with ws:// or https:// with wss://
const getWebSocketUrl = () => {
  const baseUrl = API_BASE_URL.replace(/^http/, 'ws');
  return `${baseUrl}/ws/${uuidv4()}`;
};

type WebSocketMessage = {
  type: string;
  [key: string]: any;
};

export function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [error, setError] = useState<string | null>(null);
  const socketRef = useRef<WebSocket | null>(null);

  // Initialize WebSocket connection
  useEffect(() => {
    const wsUrl = getWebSocketUrl();
    const socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      console.log('WebSocket connection established');
      setIsConnected(true);
      setError(null);
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('Received message:', data);
        setLastMessage(data);
      } catch (err) {
        console.error('Error parsing WebSocket message:', err);
        setError('Failed to parse message from server');
      }
    };

    socket.onerror = (event) => {
      console.error('WebSocket error:', event);
      setError('WebSocket connection error');
      setIsConnected(false);
    };

    socket.onclose = () => {
      console.log('WebSocket connection closed');
      setIsConnected(false);
    };

    socketRef.current = socket;

    // Clean up on unmount
    return () => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.close();
      }
    };
  }, []);

  // Send a message through the WebSocket
  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(message));
    } else {
      setError('WebSocket is not connected');
    }
  }, []);

  // Generate BrowserUse function calls
  const generateBrowserUseFunctions = useCallback((actionDescription: string) => {
    sendMessage({
      type: 'browser_use',
      action_description: actionDescription,
    });
  }, [sendMessage]);

  // Send a chat message
  const sendChatMessage = useCallback((message: string, history: any[]) => {
    sendMessage({
      type: 'chat',
      message,
      history,
    });
  }, [sendMessage]);

  return {
    isConnected,
    lastMessage,
    error,
    sendMessage,
    generateBrowserUseFunctions,
    sendChatMessage,
  };
} 