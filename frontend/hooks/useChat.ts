import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Message } from "@/components/chat/types";

export function useChat(sessionId: string) {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

  const checkAuthOrRedirect = (): boolean => {
    const isUserLogged = localStorage.getItem("user_logged_in") === "true";
    if (!isUserLogged) {
      localStorage.removeItem("user_logged_in");
      router.push("/login");
      return false;
    }
    return true;
  };

  useEffect(() => {
    const fetchChatHistory = async () => {
      if (!checkAuthOrRedirect() || !sessionId || sessionId === "undefined")
        return;

      try {
        const response = await fetch(
          `${BACKEND_URL}/chat/history?session_id=${sessionId}`,
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
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async (text: string) => {
    if (!text.trim() || loading || !checkAuthOrRedirect()) return;

    const userMessage: Message = { role: "user", content: text };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await fetch(`${BACKEND_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ message: text, session_id: sessionId }),
      });

      if (response.status === 401) {
        localStorage.removeItem("user_logged_in");
        router.push("/login");
        router.refresh();
        throw new Error("Session expired. Please log in again.");
      }

      if (!response.ok) throw new Error("Request failed");

      const reader = response.body?.getReader();
      if (!reader) throw new Error("No response stream");

      const decoder = new TextDecoder();
      setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });

        setMessages((prev) => {
          const copy = [...prev];
          const lastIndex = copy.length - 1;
          copy[lastIndex] = {
            ...copy[lastIndex],
            content: copy[lastIndex].content + chunk,
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
          content: error.message || "Something went wrong.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file: File) => {
    if (!checkAuthOrRedirect()) return;

    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        content: `Uploading and processing file "${file.name}"... Please wait.`,
      },
    ]);

    try {
      const response = await fetch(`${BACKEND_URL}/documents/upload`, {
        method: "POST",
        credentials: "include",
        body: formData,
      });

      if (response.status === 401) {
        localStorage.removeItem("user_logged_in");
        router.push("/login");
        return;
      }

      if (!response.ok) throw new Error("File upload failed.");

      const data = await response.json();
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `File "${file.name}" uploaded successfully (${data.chunks_count} chunks extracted). You can now ask questions about this document.`,
        },
      ]);
    } catch (error: any) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Error processing file: ${error.message || "An unexpected error occurred."}`,
        },
      ]);
    } finally {
      setUploading(false);
    }
  };

  return {
    messages,
    loading,
    uploading,
    messagesEndRef,
    handleSend,
    handleFileUpload,
  };
}
