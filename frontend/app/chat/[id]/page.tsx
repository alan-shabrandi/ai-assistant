"use client";

import { useParams } from "next/navigation";
import ChatArea from "@/components/chat/ChatArea";
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";

export default function ChatPage() {
  const params = useParams();
  const chatId = params.id as string;

  return (
    <main className="h-screen bg-background text-foreground overflow-hidden">
      <div className="flex h-full">
        <Sidebar />

        <section className="flex min-w-0 flex-1 flex-col">
          <div className="bg-amber-500/10 border-b border-amber-500/20 px-4 py-2 text-center text-xs md:text-sm text-amber-600 dark:text-amber-400 font-medium">
            ⚠️ <strong>Demo Project Notice:</strong> To manage resources
            effectively, standard limits are active (Max 5MB per upload, 5
            messages/min, and 15 messages per session).
          </div>

          <Header />
          <ChatArea sessionId={chatId} />
        </section>
      </div>
    </main>
  );
}
