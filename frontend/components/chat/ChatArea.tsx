"use client";

import { Spinner } from "../ui/spinner";
import ChatInput from "./ChatInput";
import ChatMessage from "./ChatMessage";
import EmptyState from "./EmptyState";
import { useChat } from "@/hooks/useChat";
import { FileText } from "lucide-react";

interface ChatAreaProps {
  sessionId: string;
}

export default function ChatArea({ sessionId }: ChatAreaProps) {
  const {
    messages,
    loading,
    uploading,
    hasFiles,
    messagesEndRef,
    handleSend,
    handleFileUpload,
  } = useChat(sessionId);

  return (
    <div className="flex h-[calc(100vh-64px)] flex-col">
      {hasFiles && (
        <div className="border-b bg-background px-6 py-2.5 flex justify-between items-center transition-all">
          <div className="flex items-center gap-2 text-muted-foreground text-xs">
            <FileText className="h-4 w-4 text-emerald-500" />
            <span>Documents and files for this session have been loaded.</span>
          </div>

          <span className="flex items-center gap-1.5 text-[11px] font-medium bg-emerald-50 text-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-400 px-2.5 py-1 rounded-full border border-emerald-200 dark:border-emerald-900/40 select-none">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
            Context Active
          </span>
        </div>
      )}

      <div className="flex-1 overflow-y-auto">
        <div className="mx-auto flex max-w-4xl flex-col gap-6 px-6 py-8 pb-40">
          {messages.length === 0 ? (
            <EmptyState />
          ) : (
            <>
              {messages.map((message, index) => (
                <div className="relative" key={index}>
                  {index === messages.length - 1 && loading && (
                    <Spinner className="absolute -left-5 top-2.5" />
                  )}
                  <ChatMessage message={message} />
                </div>
              ))}
            </>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      <ChatInput
        loading={loading}
        onSend={handleSend}
        onFileUpload={handleFileUpload}
        uploading={uploading}
      />
    </div>
  );
}
