import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Message } from "@/components/chat/types";
import { toast } from "sonner";

export function useChat(sessionId: string) {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [hasFiles, setHasFiles] = useState(false);
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
          toast.error("Session expired. Please log in again.");
          localStorage.removeItem("user_logged_in");
          router.push("/login");
          return;
        }

        if (response.ok) {
          const data = await response.json();
          setMessages(data.history || []);
          setHasFiles(data.has_files || false);
        } else {
          toast.error("Failed to load chat history from server.");
        }
      } catch (error) {
        console.error("Failed to fetch chat history:", error);
        toast.error("Network error: Could not load chat history.");
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
        toast.error("Session expired. Please log in again.");
        localStorage.removeItem("user_logged_in");
        router.push("/login");
        router.refresh();
        throw new Error("Session expired.");
      }

      if (response.status === 429) {
        toast.warning("Rate limit exceeded. Please wait a minute.");
        throw new Error("Too many requests. Please slow down.");
      }

      if (response.status === 403) {
        toast.error("Demo limit reached for this session.");
        throw new Error("Session chat limit reached.");
      }

      if (!response.ok) {
        toast.error("Server encountered an error.");
        throw new Error("Request failed");
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error("No response stream");

      const decoder = new TextDecoder();
      setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        let currentChunkText = "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const content = line.substring(6);
            currentChunkText += content;
          }
        }

        if (currentChunkText) {
          setMessages((prev) => {
            const copy = [...prev];
            const lastIndex = copy.length - 1;
            copy[lastIndex] = {
              ...copy[lastIndex],
              content: copy[lastIndex].content + currentChunkText,
            };
            return copy;
          });
        }
      }
    } catch (error: any) {
      console.error(error);
      if (
        error.message !== "Session expired." &&
        error.message !== "Too many requests. Please slow down." &&
        error.message !== "Session chat limit reached."
      ) {
        toast.error("Failed to connect to the server.");
      }
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
    formData.append("session_id", sessionId);

    const uploadToastId = toast.loading(`Uploading "${file.name}"...`);

    try {
      const response = await fetch(`${BACKEND_URL}/documents/upload`, {
        method: "POST",
        credentials: "include",
        body: formData,
      });

      if (response.status === 401) {
        toast.error("Session expired.", { id: uploadToastId });
        localStorage.removeItem("user_logged_in");
        router.push("/login");
        return;
      }

      if (!response.ok) {
        toast.error("File processing failed on server.", { id: uploadToastId });
        throw new Error("File upload failed.");
      }

      const data = await response.json();
      toast.success("Document processed successfully!", { id: uploadToastId });
      setHasFiles(true);
    } catch (error: any) {
      console.error(error);
    } finally {
      setUploading(false);
    }
  };

  return {
    messages,
    loading,
    uploading,
    hasFiles,
    messagesEndRef,
    handleSend,
    handleFileUpload,
  };
}
