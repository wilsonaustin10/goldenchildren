'use client';

/* eslint-disable @typescript-eslint/no-unused-vars */
import { useRef, useState } from "react";
import { Sender, Message } from "../types/Message";
import { API_BASE_URL } from "@/api/base";

const DEFAULT_MESSAGE = {
    text: "",
    sender: Sender.AI
};

export function useChatbot() {
    const [messages, setMessages] = useState<Message[]>([]);

    /**
     * We maintain a state for currMessage because
     * 1. setState triggers a re-render, which notifies other components using this hook that the currMessage value has changed
     */
    const [currMessage, setCurrMessage] = useState<Message>(DEFAULT_MESSAGE);
    const [isGenerating, setIsGenerating] = useState(false);
    
    const sendMessage = async (message: string) => {
        try {
            setMessages((prev) => [...prev, { text: message, sender: Sender.USER }])
            setIsGenerating(_ => true);
            // Note: axios does not support streaming by default
            const res = await fetch(`${API_BASE_URL}/chat`, {
                method: "POST",
                body: JSON.stringify({ 
                    message: message,
                    history: messages
                }),
                headers: {
                    'Accept': "text/event-stream,application/json",
                    "Content-Type": "application/json",
                }
            })
            
            if (res.body === null) return console.error("FAILED");

            const data = await res.json();
            console.log(data);
            if (data.needs_more_info) {
                setMessages(prev => [...prev, { 
                    text: data.content, 
                    sender: Sender.AI 
                }]);
            } else {
                setMessages(prev => [...prev, { 
                    text: `${data.content}`, 
                    sender: Sender.AI 
                }]);
            }
            
            // setMessages(prev => {
            //         const currentMessage: Message = {text: aiMessage, sender: Sender.AI};
            //     return [...prev, currentMessage];
            // });
            // Reset the current mesage to hide it
            // setCurrMessage(_ => DEFAULT_MESSAGE);

        } catch (ex) {
            console.error('Error sending message:', ex)
            setMessages(prev => {
                return [...prev, { text: "Error: No response from server", sender: Sender.AI }];
            });
        } finally {
            setIsGenerating(_ => false);
        }
    }

    return {
        messages,
        currMessage,
        sendMessage,
        isGenerating,
    }
}