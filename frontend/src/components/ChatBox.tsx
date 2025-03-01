'use client';

import { Message, Sender } from "@/types/Message";
import ChatMessage from "./ChatMessage";
import ChatWidgetForm, { formSchema } from "./ChatWidgetForm";
import { FancyLoadingIndicator } from "./FancyLoadingIndicator";
import { z } from "zod";
import { useEffect, useRef } from "react";

type P = {
    messages: Message[];
    currMessage: Message;
    onSubmit: (values: string) => void;
    loading: boolean;
    className?: string;
}

export default function ChatBox(props: P) {

    const {messages, currMessage, onSubmit: sendMessage, loading: isGenerating, className } = props;
    const latestMessageRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        // auto-scroll for messages on sendMessage and another time when message is completed
        if (messages.length === 0) return;
        const lastMessage = messages[messages.length - 1];
        if (lastMessage.sender === Sender.USER || currMessage) {
            latestMessageRef.current?.scrollIntoView({ behavior: "smooth" });
        }
    }, [messages])

    const onSubmit = async (values: z.infer<typeof formSchema>) => {
        sendMessage(values.text);
    }
    return (
        <div className='w-full p-2 py-4 h-full flex flex-col'>
            <div className={`flex flex-col space-y-2 py-2 min-h-[200px] ${className ?? ""} overflow-y h-full mb-4 rounded overflow-y-auto overflow-x-hidden`}>
                {messages.map((message, index) => (
                    <ChatMessage 
                    key={index}
                    message={message} />
                ))}
                {/* Hide the currMessage if its text is null */}
                {currMessage.text ? <ChatMessage 
                    message={currMessage}/> : null}
                {/* Show loading indicator when generating and no current message */}
                {isGenerating && !currMessage.text && <FancyLoadingIndicator />}
                <div ref={latestMessageRef}></div> 
            </div>
            <ChatWidgetForm 
                messages={messages}
                isGenerating={isGenerating}
                onSubmit={onSubmit} />
        </div>
    )
}