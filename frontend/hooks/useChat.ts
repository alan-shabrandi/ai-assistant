import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Message } from "@/components/chat/types";
import { toast } from "sonner";
import { apiClient } from "@/lib/api-client";

export function useChat(sessionId: string) {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [hasFiles, setHasFiles] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

  const handleUnauthorized = () => {
    localStorage.removeItem("user_logged_in");
    router.push("/login");
    router.refresh();
  };

  const checkAuthOrRedirect = (): boolean => {
    const isUserLogged = localStorage.getItem("user_logged_in") === "true";
    if (!isUserLogged) {
      handleUnauthorized();
      return false;
    }
    return true;
  };

  useEffect(() => {
    const fetchChatHistory = async () => {
      if (!checkAuthOrRedirect() || !sessionId || sessionId === "undefined")
        return;

      try {
        const response = await apiClient.get(`/chat/history`, {
          params: { session_id: sessionId },
        });

        setMessages(response.data.history || []);
        setHasFiles(response.data.has_files || false);
      } catch (error: any) {
        console.error("Failed to fetch chat history:", error);

        if (error.response?.status === 401) {
          toast.error("Session expired. Please log in again.");
          handleUnauthorized();
        } else {
          toast.error("Failed to load chat history from server.");
        }
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

      if (!response.ok) {
        if (response.status === 401) {
          toast.error("Session expired. Please log in again.");
          handleUnauthorized();
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
            currentChunkText += line.substring(6);
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
      const standardErrors = [
        "Session expired.",
        "Too many requests. Please slow down.",
        "Session chat limit reached.",
      ];

      if (!standardErrors.includes(error.message)) {
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
      await apiClient.post("/documents/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      toast.success("Document processed successfully!", { id: uploadToastId });
      setHasFiles(true);
    } catch (error: any) {
      console.error(error);

      if (error.response?.status === 401) {
        toast.error("Session expired.", { id: uploadToastId });
        handleUnauthorized();
      } else {
        toast.error("File processing failed on server.", { id: uploadToastId });
      }
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
