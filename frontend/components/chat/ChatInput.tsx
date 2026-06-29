"use client";

import { useEffect, useRef, useState } from "react";
import { ArrowUp, Paperclip, Loader2, FileText } from "lucide-react";

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
  const canSend = message.trim() && !isActionDisabled;

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
    <div className="border-t bg-background/90 backdrop-blur-sm sticky bottom-0 z-10">
      <div className="mx-auto max-w-3xl px-4 py-4 md:py-6">
        {uploading && (
          <div className="mb-2 mx-1 flex items-center gap-2.5 px-3 py-2 text-xs rounded-xl border bg-muted/40 animate-in fade-in slide-in-from-bottom-2 duration-200">
            <div className="p-1 rounded-md bg-primary/10 text-primary">
              <FileText className="h-3.5 w-3.5" />
            </div>
            <span className="text-muted-foreground font-medium animate-pulse">
              Processing and indexing PDF document...
            </span>
            <Loader2 className="h-3 w-3 animate-spin text-muted-foreground ml-auto" />
          </div>
        )}

        <div className="flex items-center gap-2 rounded-2xl border bg-muted/30 focus-within:bg-background focus-within:ring-1 focus-within:ring-ring focus-within:border-ring p-2 px-3 shadow-sm transition-all duration-200">
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
            className="h-9 w-9 shrink-0 rounded-xl cursor-pointer hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
          >
            <Paperclip className="h-4 w-4" />
          </Button>

          <Textarea
            ref={textareaRef}
            rows={1}
            autoFocus
            disabled={isActionDisabled}
            value={message}
            placeholder="Message AI or upload PDF..."
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            className="
              max-h-48
              min-h-9
              py-2
              resize-none
              border-0
              bg-transparent
              p-0
              text-sm
              shadow-none
              focus-visible:ring-0
              focus-visible:ring-offset-0
              placeholder:text-muted-foreground/60
              pt-2
            "
          />

          <Button
            size="icon"
            onClick={handleSend}
            disabled={!canSend}
            className={`h-9 w-9 shrink-0 rounded-xl cursor-pointer transition-all duration-200 ${
              canSend
                ? "bg-primary text-primary-foreground hover:opacity-90 shadow-sm scale-100"
                : "bg-muted text-muted-foreground/40 scale-95"
            }`}
          >
            <ArrowUp className="h-4 w-4" />
          </Button>
        </div>

        <p className="mt-2.5 text-center text-[11px] text-muted-foreground/70 tracking-wide">
          AI can make mistakes. Verify important information.
        </p>
      </div>
    </div>
  );
}
