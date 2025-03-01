'use client';

import Markdown from "react-markdown";
import { Message, Sender } from "../types/Message";
import remarkGfm from 'remark-gfm'
import { cn } from "@/lib/utils";

type P = {
    message: Message;
}

export default function ChatMessage({message}: P) {
    const isSender = message.sender === Sender.USER;

    return (
          <div className={cn(
            `border rounded py-2 px-4 max-w-[75%]`,
            isSender ? "self-end mr-2 bg-green-500 text-white": "self-start ml-2 bg-white"
          )}>
          <Markdown remarkPlugins={[remarkGfm]}>
          {message.text}
          </Markdown>
      </div>
    )
}