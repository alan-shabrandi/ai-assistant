"use client";

import ChatInput from "./ChatInput";
import ChatMessage from "./ChatMessage";
import EmptyState from "./EmptyState";
import TypingIndicator from "./TypingIndicator";
import { useChat } from "@/hooks/useChat";

interface ChatAreaProps {
  sessionId: string;
}

export default function ChatArea({ sessionId }: ChatAreaProps) {
  const {
    messages,
    loading,
    uploading,
    messagesEndRef,
    handleSend,
    handleFileUpload,
  } = useChat(sessionId);

  return (
    <div className="flex h-[calc(100vh-64px)] flex-col">
      <div className="flex-1 overflow-y-auto">
        <div className="mx-auto flex max-w-4xl flex-col gap-6 px-6 py-8 pb-40">
          {messages.length === 0 ? (
            <EmptyState />
          ) : (
            <>
              {messages.map((message, index) => (
                <ChatMessage key={index} message={message} />
              ))}

              {loading && <TypingIndicator />}
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
