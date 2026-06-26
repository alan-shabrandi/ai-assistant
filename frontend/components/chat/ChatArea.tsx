"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

import ChatInput from "./ChatInput";
import ChatMessage from "./ChatMessage";
import EmptyState from "./EmptyState";
import TypingIndicator from "./TypingIndicator";
import { Message } from "./types";
interface ChatAreaProps {
  sessionId: string;
}

export default function ChatArea({ sessionId }: ChatAreaProps) {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchChatHistory = async () => {
      const isUserLogged = localStorage.getItem("user_logged_in") === "true";
      if (!isUserLogged || !sessionId || sessionId === "undefined") return;
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_BACKEND_URL}/chat/history?session_id=${sessionId}`,
          {
            method: "GET",
            credentials: "include",
          },
        );

        if (response.status === 401) {
          localStorage.removeItem("user_logged_in");
          router.push("/login");
          return;
        }

        if (response.ok) {
          const data = await response.json();
          setMessages(data.history || []);
        }
      } catch (error) {
        console.error("Failed to fetch chat history:", error);
      }
    };

    fetchChatHistory();
  }, [sessionId, router]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  const handleSend = async (text: string) => {
    if (!text.trim() || loading) return;

    const isUserLogged = localStorage.getItem("user_logged_in") === "true";
    if (!isUserLogged) {
      router.push("/login");
      return;
    }

    const userMessage: Message = {
      role: "user",
      content: text,
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({
            message: text,
            session_id: sessionId,
          }),
        },
      );

      if (response.status === 401) {
        localStorage.removeItem("user_logged_in");
        router.push("/login");
        router.refresh();
        throw new Error("Session expired. Please log in again.");
      }

      if (!response.ok) {
        throw new Error("Request failed");
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error("No response stream");
      }

      const decoder = new TextDecoder();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "",
        },
      ]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, {
          stream: true,
        });

        setMessages((prev) => {
          const copy = [...prev];
          copy[copy.length - 1] = {
            ...copy[copy.length - 1],
            content: copy[copy.length - 1].content + chunk,
          };
          return copy;
        });
      }
    } catch (error: any) {
      console.error(error);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: error.message || "Something went wrong. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-64px)] flex-col">
      <div className="flex-1 overflow-y-auto">
        <div className="mx-auto flex max-w-4xl flex-col gap-6 px-6 py-8 pb-40">
          {messages.length === 0 ? (
            <EmptyState />
          ) : (
            <>
              {messages.map((message, index) => (
                <ChatMessage key={index} message={message} />
              ))}

              {loading && <TypingIndicator />}
            </>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      <ChatInput loading={loading} onSend={handleSend} />
    </div>
  );
}
