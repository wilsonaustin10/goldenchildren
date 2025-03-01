'use client';

/* eslint-disable @typescript-eslint/no-unused-vars */
import { useEffect, useRef, useState, useCallback } from "react";
import { Sender, Message } from "../types/Message";
import { API_BASE_URL } from "@/api/base";
import { useWebSocket } from "./useWebSocket";

const DEFAULT_MESSAGE = {
    text: "",
    sender: Sender.AI
};

export function useChatbot() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [currMessage, setCurrMessage] = useState<Message>(DEFAULT_MESSAGE);
    const [isGenerating, setIsGenerating] = useState(false);
    const [browserUsePlan, setBrowserUsePlan] = useState<any>(null);
    
    // Use the WebSocket hook
    const { 
        isConnected, 
        lastMessage, 
        error, 
        sendChatMessage, 
        generateBrowserUseFunctions 
    } = useWebSocket();
    
    // Handle incoming WebSocket messages
    useEffect(() => {
        if (lastMessage) {
            if (lastMessage.type === 'chat_response') {
                setMessages(prev => [...prev, { 
                    text: lastMessage.content, 
                    sender: Sender.AI 
                }]);
                
                if (lastMessage.browser_use_plan) {
                    setBrowserUsePlan(lastMessage.browser_use_plan);
                }
                
                setIsGenerating(false);
            } else if (lastMessage.type === 'browser_use_plan') {
                setBrowserUsePlan(lastMessage.plan);
                setIsGenerating(false);
            } else if (lastMessage.type === 'error') {
                setMessages(prev => [...prev, { 
                    text: `Error: ${lastMessage.message}`, 
                    sender: Sender.AI 
                }]);
                setIsGenerating(false);
            }
        }
    }, [lastMessage]);
    
    // Handle WebSocket connection errors
    useEffect(() => {
        if (error) {
            setMessages(prev => [...prev, { 
                text: `Connection error: ${error}. Falling back to HTTP.`, 
                sender: Sender.AI 
            }]);
        }
    }, [error]);
    
    const sendMessage = async (message: string) => {
        try {
            // Add user message to the chat
            setMessages((prev) => [...prev, { text: message, sender: Sender.USER }]);
            setIsGenerating(true);
            
            // Try to use WebSocket if connected
            if (isConnected) {
                // Convert messages to the format expected by the backend
                const history = messages.map(msg => ({
                    role: msg.sender === Sender.USER ? 'user' : 'assistant',
                    content: msg.text
                }));
                
                // Send the message via WebSocket
                sendChatMessage(message, history);
            } else {
                // Fallback to HTTP if WebSocket is not connected
                const res = await fetch(`${API_BASE_URL}/chat/browser-use`, {
                    method: "POST",
                    body: JSON.stringify({ 
                        message: message,
                        history: messages
                    }),
                    headers: {
                        'Accept': "application/json",
                        "Content-Type": "application/json",
                    }
                });
                
                if (res.body === null) {
                    throw new Error("Failed to get response from server");
                }

                const data = await res.json();
                
                if (data.needs_more_info) {
                    setMessages(prev => [...prev, { 
                        text: data.content, 
                        sender: Sender.AI 
                    }]);
                } else {
                    setMessages(prev => [...prev, { 
                        text: data.content, 
                        sender: Sender.AI 
                    }]);
                    
                    if (data.browser_use_plan) {
                        setBrowserUsePlan(data.browser_use_plan);
                    }
                }
                
                setIsGenerating(false);
            }
        } catch (ex) {
            console.error('Error sending message:', ex);
            setMessages(prev => {
                return [...prev, { text: "Error: No response from server", sender: Sender.AI }];
            });
            setIsGenerating(false);
        }
    };
    
    // Function to directly generate BrowserUse function calls
    const generateBrowserUse = async (actionDescription: string) => {
        try {
            setIsGenerating(true);
            
            // Try to use WebSocket if connected
            if (isConnected) {
                generateBrowserUseFunctions(actionDescription);
            } else {
                // Fallback to HTTP if WebSocket is not connected
                const res = await fetch(`${API_BASE_URL}/api/browser-use`, {
                    method: "POST",
                    body: JSON.stringify({ 
                        action_description: actionDescription
                    }),
                    headers: {
                        'Accept': "application/json",
                        "Content-Type": "application/json",
                    }
                });
                
                if (res.body === null) {
                    throw new Error("Failed to get response from server");
                }

                const data = await res.json();
                setBrowserUsePlan(data);
                setIsGenerating(false);
            }
        } catch (ex) {
            console.error('Error generating BrowserUse functions:', ex);
            setIsGenerating(false);
        }
    };

    return {
        messages,
        currMessage,
        sendMessage,
        isGenerating,
        browserUsePlan,
        generateBrowserUse,
        isWebSocketConnected: isConnected
    };
}