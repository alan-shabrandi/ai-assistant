"use client";

import { useEffect, useRef, useState } from "react";
import { ArrowUp } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

interface ChatInputProps {
  loading: boolean;
  onSend: (message: string) => void;
}

export default function ChatInput({ loading, onSend }: ChatInputProps) {
  const [message, setMessage] = useState("");

  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (!textareaRef.current) return;

    textareaRef.current.style.height = "0px";
    textareaRef.current.style.height = textareaRef.current.scrollHeight + "px";
  }, [message]);

  const handleSend = () => {
    const text = message.trim();

    if (!text || loading) return;

    onSend(text);

    setMessage("");

    requestAnimationFrame(() => {
      if (textareaRef.current) {
        textareaRef.current.style.height = "56px";
      }
    });
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t bg-background">
      <div className="mx-auto max-w-4xl p-4">
        <div className="flex items-end gap-2 rounded-3xl border bg-background p-3 shadow-sm">
          <Textarea
            ref={textareaRef}
            rows={1}
            autoFocus
            disabled={loading}
            value={message}
            placeholder="Message AI..."
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            className="
              max-h-48
              min-h-[56px]
              resize-none
              border-0
              bg-transparent
              p-0
              shadow-none
              focus-visible:ring-0
              focus-visible:ring-offset-0
            "
          />

          <Button
            size="icon"
            onClick={handleSend}
            disabled={!message.trim() || loading}
            className="h-10 w-10 rounded-full"
          >
            <ArrowUp className="h-4 w-4" />
          </Button>
        </div>

        <p className="mt-3 text-center text-xs text-muted-foreground">
          AI can make mistakes. Verify important information.
        </p>
      </div>
    </div>
  );
}
