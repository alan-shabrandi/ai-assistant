"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { Plus, Settings, Loader2, MessageSquare } from "lucide-react";

import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";

import { apiClient } from "@/lib/api-client";
import { useAuth } from "@/context/auth-context";
import { SidebarChatItem } from "./SidebarChatItem";

interface ChatSession {
  session_id: string;
  title: string;
}

export default function Sidebar() {
  const router = useRouter();
  const params = useParams();
  const currentSessionId = params.id as string;

  const { isLoggedIn, checkingAuth } = useAuth();
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    const fetchSessions = async () => {
      if (!isLoggedIn) return;
      try {
        setIsLoading(true);
        const response = await apiClient.get<{ sessions: ChatSession[] }>(
          "/chat/sessions",
        );
        setSessions(response.data.sessions || []);
      } catch (error) {
        console.error("Failed to fetch chat sessions:", error);
      } finally {
        setIsLoading(false);
      }
    };

    if (!checkingAuth) {
      fetchSessions();
    }
  }, [isLoggedIn, checkingAuth]);

  const handleNewChat = () => {
    const newChatId = crypto.randomUUID();
    router.push(`/chat/${newChatId}`);
  };

  const handleDeleteSession = async (sessionId: string) => {
    try {
      setDeletingId(sessionId);
      await apiClient.delete(`/chat/session/${sessionId}`);
      setSessions((prev) => prev.filter((s) => s.session_id !== sessionId));

      if (currentSessionId === sessionId) {
        router.push("/chat");
      }
    } catch (error) {
      console.error("Error deleting session:", error);
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <aside className="hidden w-72 shrink-0 border-r bg-muted/30 md:flex md:flex-col transition-all duration-300">
      <div className="p-3.5 pb-2">
        <Button
          onClick={handleNewChat}
          variant="outline"
          className="w-full justify-start gap-2 bg-background hover:bg-muted border-dashed border-muted-foreground/30 shadow-sm transition-all duration-200 group active:scale-[0.98]"
        >
          <Plus className="h-4 w-4 text-muted-foreground group-hover:text-foreground transition-colors" />
          <span className="font-medium text-sm">New Chat</span>
        </Button>
      </div>

      <ScrollArea className="flex-1 px-3 py-2">
        <div className="space-y-6">
          <div className="min-w-0 overflow-hidden">
            <p className="mb-2 px-2 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground/80 select-none">
              Recent Chats
            </p>

            <div className="space-y-1 min-w-0 overflow-hidden">
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-4 w-4 animate-spin text-muted-foreground/70" />
                </div>
              ) : sessions.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-8 px-2 text-center border border-dashed rounded-lg border-muted/60 bg-background/30 m-1">
                  <MessageSquare className="h-4 w-4 text-muted-foreground/40 mb-1" />
                  <p className="text-xs text-muted-foreground/70 italic">
                    No history found
                  </p>
                </div>
              ) : (
                sessions.map((session) => (
                  <SidebarChatItem
                    key={session.session_id}
                    sessionId={session.session_id}
                    title={session.title}
                    isActive={currentSessionId === session.session_id}
                    isDeleting={deletingId === session.session_id}
                    onDelete={handleDeleteSession}
                  />
                ))
              )}
            </div>
          </div>
        </div>
      </ScrollArea>

      <Separator className="opacity-60" />

      <div className="p-2 bg-background/20">
        <Button
          variant="ghost"
          className="w-full justify-start gap-2 h-10 px-3 hover:bg-muted rounded-lg text-muted-foreground hover:text-foreground group transition-colors"
        >
          <Settings className="h-4 w-4 text-muted-foreground group-hover:rotate-45 transition-transform duration-300" />
          <span className="text-sm font-medium">Settings</span>
        </Button>
      </div>
    </aside>
  );
}
