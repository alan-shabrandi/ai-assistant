"use client";

import { Bot } from "lucide-react";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";

import { Card } from "@/components/ui/card";

export default function TypingIndicator() {
  return (
    <div className="flex items-start gap-4">
      <Avatar className="h-9 w-9">
        <AvatarFallback>
          <Bot className="h-4 w-4" />
        </AvatarFallback>
      </Avatar>

      <Card className="rounded-2xl px-4 py-3">
        <div className="flex items-center gap-1">
          <span
            className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground"
            style={{ animationDelay: "0ms" }}
          />

          <span
            className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground"
            style={{ animationDelay: "150ms" }}
          />

          <span
            className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground"
            style={{ animationDelay: "300ms" }}
          />
        </div>
      </Card>
    </div>
  );
}
