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
            const res = await fetch(`${API_BASE_URL}`, {
                method: "POST",
                body: JSON.stringify({ query: message }),
                headers: {
                    'Accept': "text/event-stream,application/json",
                    "Content-Type": "application/json",
                }
            })
            
            if (res.body === null) return console.error("FAILED");
            const reader = res.body.getReader();
            const decoder = new TextDecoder("utf-8");

            let aiMessage = "";
            while (true) {
                const { done, value, } = await reader.read();
                console.log(done, value);
                if (done) {
                    break;
                }
                const decodedValue = decoder.decode(value);
                aiMessage += decodedValue;

                // We update it now so as to trigger a rerender
                setCurrMessage((prev) => {
                    return {
                        sender: prev.sender,
                        text: prev.text + decodedValue,
                    }
                });

            }
            
            if (aiMessage === "") {
                // When endpoint fails, no error message is returned due to it being an
                setMessages(prev => {                 
                    return [...prev, { text: "Error: No response from server", sender: Sender.AI }];
                })
            } else {
                setMessages(prev => {
                        const currentMessage: Message = {text: aiMessage, sender: Sender.AI};
                    return [...prev, currentMessage];
                });
            }
            // Reset the current mesage to hide it
            setCurrMessage(_ => DEFAULT_MESSAGE);

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