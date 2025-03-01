'use client'

import ChatBox from "@/components/ChatBox";
import { useChatbot } from "@/hooks/useChatbot";

export default function Home() {
  const {messages, currMessage, sendMessage, isGenerating} = useChatbot();

  return (
    <div className="flex items-center">
      <div className="flex flex-col justify-end w-1/3 h-screen bg-gray-700">
        <ChatBox
          messages={messages}
          currMessage={currMessage}
          onSubmit={sendMessage}
          loading={isGenerating}
           />
      </div>
      <div className="w-2/3 h-screen bg-gray-600"></div>
    </div>
  );
}
