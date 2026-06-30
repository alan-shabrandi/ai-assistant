"use client";

import { useParams } from "next/navigation";
import ChatArea from "@/components/chat/ChatArea";
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/sidebar/Sidebar";
import FreeTierModal from "@/components/modals/FreeTierModal";

export default function ChatPage() {
  const params = useParams();
  const chatId = params.id as string;

  return (
    <main className="h-screen bg-background text-foreground overflow-hidden relative">
      <div className="flex h-full">
        <Sidebar />

        <section className="flex min-w-0 flex-1 flex-col">
          <Header />
          <ChatArea sessionId={chatId} />
        </section>
      </div>

      <FreeTierModal />
    </main>
  );
}
