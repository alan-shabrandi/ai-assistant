"use client";

import { useEffect, useRef, useState } from "react";
import { ArrowUp, Paperclip } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

interface ChatInputProps {
  loading: boolean;
  onSend: (message: string) => void;
  onFileUpload?: (file: File) => Promise<void>;
  uploading?: boolean;
}

export default function ChatInput({
  loading,
  onSend,
  onFileUpload,
  uploading = false,
}: ChatInputProps) {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const isActionDisabled = loading || uploading;

  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    textarea.style.height = "auto";
    textarea.style.height = `${textarea.scrollHeight}px`;
  }, [message]);

  const handleSend = () => {
    const text = message.trim();
    if (!text || isActionDisabled) return;

    onSend(text);
    setMessage("");

    requestAnimationFrame(() => {
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    });
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.nativeEvent.isComposing) return;

    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && onFileUpload) {
      await onFileUpload(file);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const triggerFileSelect = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="border-t bg-background">
      <div className="mx-auto max-w-4xl p-4">
        <div className="flex items-end gap-2 rounded-3xl border bg-background p-3 shadow-sm">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".pdf"
            className="hidden"
            disabled={isActionDisabled}
          />

          <Button
            type="button"
            size="icon"
            variant="ghost"
            onClick={triggerFileSelect}
            disabled={isActionDisabled}
            className="h-10 w-10 shrink-0 rounded-full cursor-pointer"
          >
            <Paperclip
              className={`h-5 w-5 ${uploading ? "animate-pulse text-muted-foreground" : ""}`}
            />
          </Button>

          <Textarea
            ref={textareaRef}
            rows={1}
            autoFocus
            disabled={isActionDisabled}
            value={message}
            placeholder={
              uploading
                ? "Uploading and indexing PDF..."
                : "Message AI or upload PDF..."
            }
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            className="
              max-h-48
              min-h-14
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
            disabled={!message.trim() || isActionDisabled}
            className="h-10 w-10 shrink-0 rounded-full cursor-pointer"
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
