'use client';

import ChatBox from "@/components/ChatBox";
import { useChatbot } from "@/hooks/useChatbot";
import Head from "next/head";

export default function Home() {
    const { messages, currMessage, sendMessage, isGenerating } = useChatbot();
    return (
        <div className="flex flex-col items-center min-h-screen bg-black relative overflow-hidden">
            <Head>
                <title>Create Your Agent</title>
                <meta name="description" content="Create your own agent" />
                <link rel="icon" href="/favicon.ico" />
            </Head>

            {/* Background effects positioned behind content */}
            <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:40px_40px] pointer-events-none" />
            <div className="absolute h-40 w-40 rounded-full bg-purple-600/20 -top-20 -right-20 blur-3xl" />
            <div className="absolute h-40 w-40 rounded-full bg-blue-600/20 bottom-20 -left-20 blur-3xl" />
            
            {/* Header section with fixed height */}
            <div className="w-full py-16 px-4">
                <div className="text-center">
                    <h1 className="text-5xl md:text-7xl font-extrabold tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-500 mb-8">
                        Create Your Agent
                    </h1>
                    <div className="text-xl font-bold text-neutral-400">Tell us what you want your agent to do below</div>
                </div>
            </div>
            
            {/* ChatBox container with flex-grow */}
            <div className="w-full max-w-3xl px-4 pb-8 flex-grow">
                <ChatBox
                  className="max-h-[400px]"
                    messages={messages}
                    currMessage={currMessage}
                    onSubmit={sendMessage}
                    loading={isGenerating}
                />
            </div>
        </div>
    )
}