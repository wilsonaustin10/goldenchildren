'use client'

import ChatBox from "@/components/ChatBox";
import { useChatbot } from "@/hooks/useChatbot";
import BrowserUsePlan from "@/components/BrowserUsePlan";

export default function Chat() {
  const {
    messages, 
    currMessage, 
    sendMessage, 
    isGenerating, 
    browserUsePlan,
    isWebSocketConnected
  } = useChatbot();

  return (
    <div className="flex items-center">
      <div className="flex flex-col justify-end w-1/3 h-screen bg-neutral-700">
        {isWebSocketConnected && (
          <div className="px-4 py-2 text-sm text-green-500">
            WebSocket Connected
          </div>
        )}
        <ChatBox
          messages={messages}
          currMessage={currMessage}
          onSubmit={sendMessage}
          loading={isGenerating}
        />
      </div>
      <div className="w-1/3 h-screen bg-neutral-700">
          <BrowserUsePlan plan={browserUsePlan} />
      </div>
      <div className="w-2/3 h-screen bg-neutral-800">
        <iframe src="http://localhost:6080/vnc.html" className="w-full h-full" />
      </div>
    </div>
  );
}
