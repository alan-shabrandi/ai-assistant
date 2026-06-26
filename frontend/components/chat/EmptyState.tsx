"use client";

import { Sparkles } from "lucide-react";

export default function EmptyState() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center px-6">
      <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
        <Sparkles className="h-8 w-8 text-primary" />
      </div>

      <h1 className="text-3xl font-semibold tracking-tight">
        How can I help you today?
      </h1>

      <p className="mt-3 max-w-md text-center text-sm leading-6 text-muted-foreground">
        Ask anything about programming, AI, writing, research, or any other
        topic. I&apos;m here to help.
      </p>
    </div>
  );
}
