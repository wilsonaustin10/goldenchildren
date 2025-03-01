'use client';

import Markdown from "react-markdown";
import { Message, Sender } from "../types/Message";
import remarkGfm from 'remark-gfm'
import { cn } from "@/lib/utils";
import Link from "next/link";

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
          
          {/* {!message.needsMoreInfo  */}
          {message.needsMoreInfo != null && !message.needsMoreInfo 
            ? <div className="">
                <hr className="my-2"/>
                <p className="mb-2">Is this what you meant?</p>
                <div className="flex gap-x-2">
                  <Link href="/chat"><button className="cursor-pointer rounded px-4 py-2 bg-neutral-600 text-white" type="button">Yes</button></Link>
                  <button className="cursor-pointer rounded px-4 py-2 bg-neutral-600 text-white" type="button">No</button>
                </div>
              </div>
            : null
          }
      </div>
    )
}