"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { Plus, Settings, MoreHorizontal, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface ChatSession {
  session_id: string;
  title: string;
}

export default function Sidebar() {
  const router = useRouter();
  const params = useParams();
  const currentSessionId = params.id as string;

  const [sessions, setSessions] = useState<ChatSession[]>([]);

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

  useEffect(() => {
    fetchSessions();
  }, [currentSessionId]);

  const handleNewChat = () => {
    const newChatId = crypto.randomUUID();
    router.push(`/chat/${newChatId}`);
  };

  const handleDeleteSession = async (
    e: React.MouseEvent,
    sessionId: string,
  ) => {
    e.stopPropagation();

    if (!confirm("Are you sure you want to delete this chat?")) return;

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/chat/session/${sessionId}`,
        {
          method: "DELETE",
          credentials: "include",
        },
      );

      if (response.ok) {
        setSessions((prev) => prev.filter((s) => s.session_id !== sessionId));

        if (currentSessionId === sessionId) {
          router.push("/chat");
        }
      } else {
        console.error("Failed to delete session on server");
      }
    } catch (error) {
      console.error("Error deleting session:", error);
    }
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
                  <div
                    key={session.session_id}
                    className="group relative flex items-center"
                  >
                    <Button
                      variant={
                        currentSessionId === session.session_id
                          ? "secondary"
                          : "ghost"
                      }
                      className="w-full justify-start gap-2 pr-8 truncate text-right"
                      onClick={() => router.push(`/chat/${session.session_id}`)}
                    >
                      <span className="truncate w-full dir-rtl block">
                        {session.title || "message without name"}
                      </span>
                    </Button>

                    <div className="absolute right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button
                            variant="ghost"
                            className="h-7 w-7 p-0 hover:bg-muted cursor-pointer"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem
                            className="text-destructive focus:text-destructive focus:bg-transparent hover:bg-transparent gap-2 cursor-pointer select-none"
                            onClick={(e) =>
                              handleDeleteSession(e, session.session_id)
                            }
                          >
                            <Trash2 className="h-4 w-4" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </div>
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
