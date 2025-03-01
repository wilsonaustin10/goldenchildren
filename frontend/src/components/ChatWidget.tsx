import { useState } from "react";
import { useChatbot } from "../hooks/useChatbot"
import { z } from "zod";
import { MessageSquare, X } from "lucide-react";
import ChatBox from "./ChatBox";

type P = {

}

export default function ChatWidget({}: P) {
    const {messages, currMessage, sendMessage, isGenerating } = useChatbot();
    
    const [showChat, setShowChat] = useState(false);

    return (
        <div className="App">
            
            <button onClick={() => setShowChat(!showChat)} className="fixed bottom-4 right-4 p-2 bg-blue-500 text-white rounded-full">
                {!showChat ? <MessageSquare /> : <X className='' />}
            </button>
            {showChat 
                ? <ChatBox messages={messages} currMessage={currMessage} onSubmit={sendMessage} loading={isGenerating} />
                : null
            }
        </div>
    );
}