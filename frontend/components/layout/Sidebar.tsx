"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation"; // اضافه شدن useParams برای تشخیص چت فعال
import { MessageSquare, Plus, Settings } from "lucide-react";

import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";

// تعریف ساختار داده‌ای هر چت در سایدبار
interface ChatSession {
  session_id: string;
  title: string;
}

export default function Sidebar() {
  const router = useRouter();
  const params = useParams();
  const currentSessionId = params.id as string; // آیدی چتی که الان کاربر در آن قرار دارد

  const [sessions, setSessions] = useState<ChatSession[]>([]);

  // ۱. دریافت لیست چت‌ها از بک‌اند به محض لود شدن سایدبار
  useEffect(() => {
    const fetchSessions = async () => {
      const isUserLogged = localStorage.getItem("user_logged_in") === "true";
      if (!isUserLogged) return;

      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_BACKEND_URL}/chat/sessions`,
          {
            method: "GET",
            credentials: "include",
          },
        );

        if (response.ok) {
          const data = await response.json();
          setSessions(data.sessions || []);
        }
      } catch (error) {
        console.error("Failed to fetch chat sessions:", error);
      }
    };

    fetchSessions();
  }, [currentSessionId]);

  const handleNewChat = () => {
    const newChatId = crypto.randomUUID();
    router.push(`/chat/${newChatId}`);
  };

  return (
    <aside className="hidden w-72 shrink-0 border-r bg-background md:flex md:flex-col">
      <div className="p-4">
        <Button onClick={handleNewChat} className="w-full justify-start gap-2">
          <Plus className="h-4 w-4" />
          New Chat
        </Button>
      </div>

      <Separator />

      <ScrollArea className="flex-1 px-3 py-4">
        <div className="space-y-6">
          <div>
            <p className="mb-2 px-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
              Recent Chats
            </p>

            <div className="space-y-1">
              {sessions.length === 0 ? (
                <p className="px-2 text-xs text-muted-foreground italic">
                  not found
                </p>
              ) : (
                sessions.map((session) => (
                  <Button
                    key={session.session_id}
                    variant={
                      currentSessionId === session.session_id
                        ? "secondary"
                        : "ghost"
                    }
                    className="w-full justify-start gap-2 truncate"
                    onClick={() => router.push(`/chat/${session.session_id}`)}
                  >
                    <MessageSquare className="h-4 w-4 shrink-0" />
                    <span className="truncate text-right w-full dir-rtl">
                      {session.title || "message without name"}
                    </span>
                  </Button>
                ))
              )}
            </div>
          </div>
        </div>
      </ScrollArea>

      <Separator />

      <div className="p-3">
        <Button variant="ghost" className="w-full justify-start gap-2">
          <Settings className="h-4 w-4" />
          Settings
        </Button>
      </div>
    </aside>
  );
}
