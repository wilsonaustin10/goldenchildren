# WebSocket Integration for BrowserUse Function Calls

This document explains how to use the WebSocket functionality to communicate BrowserUse function calls between the backend and frontend.

## Overview

The system uses WebSockets to provide real-time communication of BrowserUse function calls from the backend to the frontend. This allows for a more responsive user experience compared to traditional HTTP requests.

## Backend Implementation

The backend uses FastAPI's built-in WebSocket support to handle WebSocket connections. The implementation includes:

1. A WebSocket endpoint at `/ws/{client_id}` that accepts connections from clients
2. Support for two message types:
   - `browser_use`: Generates BrowserUse function calls from a plain English action description
   - `chat`: Processes a chat message and generates a response, potentially including BrowserUse function calls

### WebSocket Message Format

#### Browser Use Request
```json
{
  "type": "browser_use",
  "action_description": "Go to Google and search for AI news"
}
```

#### Chat Request
```json
{
  "type": "chat",
  "message": "I want to search for AI news on Google",
  "history": [
    {
      "role": "user",
      "content": "Hello"
    },
    {
      "role": "assistant",
      "content": "Hi there! How can I help you today?"
    }
  ]
}
```

#### Browser Use Plan Response
```json
{
  "type": "browser_use_plan",
  "plan": {
    "functions": [
      {
        "name": "navigate",
        "args": {
          "url": "https://www.google.com"
        }
      },
      {
        "name": "type",
        "args": {
          "selector": "input[name='q']",
          "text": "AI news"
        }
      },
      {
        "name": "click",
        "args": {
          "selector": "input[name='btnK'], button[type='submit']"
        }
      }
    ],
    "explanation": "This plan navigates to Google and searches for AI news"
  }
}
```

#### Chat Response
```json
{
  "type": "chat_response",
  "content": "I'll search for AI news on Google for you",
  "needs_more_info": false,
  "browser_use_plan": {
    "functions": [
      {
        "name": "navigate",
        "args": {
          "url": "https://www.google.com"
        }
      },
      {
        "name": "type",
        "args": {
          "selector": "input[name='q']",
          "text": "AI news"
        }
      },
      {
        "name": "click",
        "args": {
          "selector": "input[name='btnK'], button[type='submit']"
        }
      }
    ],
    "explanation": "This plan navigates to Google and searches for AI news"
  }
}
```

## Frontend Implementation

The frontend uses the native WebSocket API to connect to the backend. The implementation includes:

1. A `useWebSocket` hook that manages the WebSocket connection
2. A `useChatbot` hook that uses the WebSocket connection to send messages and receive responses
3. A `BrowserUsePlan` component that displays the BrowserUse function calls

### Using the WebSocket Hook

```typescript
const { 
  isConnected, 
  lastMessage, 
  error, 
  sendMessage, 
  generateBrowserUseFunctions, 
  sendChatMessage 
} = useWebSocket();

// Generate BrowserUse function calls
generateBrowserUseFunctions("Go to Google and search for AI news");

// Send a chat message
sendChatMessage("I want to search for AI news on Google", history);
```

## Fallback to HTTP

The system includes fallback to traditional HTTP requests if the WebSocket connection is not available. This ensures that the functionality works even if WebSockets are not supported or if the connection fails.

## Running the Application

1. Start the backend server:
   ```
   cd backend
   python main.py
   ```

2. Start the frontend development server:
   ```
   cd frontend
   npm run dev
   ```

3. Open your browser to `http://localhost:3000` to use the application.

## Testing WebSocket Functionality

You can test the WebSocket functionality using the browser's developer tools:

1. Open the browser's developer console
2. Connect to the WebSocket endpoint:
   ```javascript
   const socket = new WebSocket('ws://localhost:8000/ws/test-client');
   
   socket.onopen = () => {
     console.log('WebSocket connection established');
   };
   
   socket.onmessage = (event) => {
     console.log('Received message:', JSON.parse(event.data));
   };
   
   socket.onerror = (error) => {
     console.error('WebSocket error:', error);
   };
   
   socket.onclose = () => {
     console.log('WebSocket connection closed');
   };
   ```

3. Send a message to generate BrowserUse function calls:
   ```javascript
   socket.send(JSON.stringify({
     type: 'browser_use',
     action_description: 'Go to Google and search for AI news'
   }));
   ```

4. Send a chat message:
   ```javascript
   socket.send(JSON.stringify({
     type: 'chat',
     message: 'I want to search for AI news on Google',
     history: []
   }));
   ``` 