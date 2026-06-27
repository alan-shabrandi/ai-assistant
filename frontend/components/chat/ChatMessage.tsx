"use client";

import { Bot, User } from "lucide-react";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

import { Message } from "./types";

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  const isSystemStatus =
    message.content.startsWith("⏳") ||
    message.content.startsWith("✅") ||
    message.content.startsWith("❌");

  return (
    <div
      className={cn(
        "flex w-full items-start gap-4",
        isUser ? "justify-end" : "justify-start",
      )}
    >
      {!isUser && (
        <Avatar className="h-9 w-9 shrink-0 border bg-background">
          <AvatarFallback>
            <Bot className="h-4 w-4" />
          </AvatarFallback>
        </Avatar>
      )}

      <Card
        className={cn(
          "max-w-[80%] rounded-2xl border px-4 py-3 shadow-none",
          "transition-colors",
          isUser
            ? "bg-primary text-primary-foreground"
            : isSystemStatus
              ? "bg-yellow-50/50 dark:bg-yellow-950/20 border-yellow-200 dark:border-yellow-900/50 text-foreground"
              : "bg-muted",
        )}
      >
        <p
          dir="auto"
          className="whitespace-pre-wrap wrap-break-word text-sm leading-7 text-start"
        >
          {message.content}
        </p>
      </Card>

      {isUser && (
        <Avatar className="h-9 w-9 shrink-0 border bg-background">
          <AvatarFallback>
            <User className="h-4 w-4" />
          </AvatarFallback>
        </Avatar>
      )}
    </div>
  );
}
