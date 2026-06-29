"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Sparkles, LogOut, LogIn, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useAuth } from "@/context/auth-context";
import { apiClient } from "@/lib/api-client";

export default function Header() {
  const router = useRouter();
  const { isLoggedIn, checkingAuth, logout } = useAuth();
  const [isLoggingOut, setIsLoggingOut] = useState<boolean>(false);

  const handleSignOut = async () => {
    try {
      setIsLoggingOut(true);

      await apiClient.post("/logout");

      logout();
      router.push("/login");
      router.refresh();
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      setIsLoggingOut(false);
    }
  };

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b bg-background/80 px-6 backdrop-blur supports-backdrop-filter:bg-background/60">
      <div className="flex items-center gap-3">
        <Sparkles className="h-5 w-5 text-primary" />
        <div>
          <h1 className="text-sm font-semibold">AI Assistant</h1>
          <p className="text-xs text-muted-foreground">Qwen-2.5 Powered</p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {checkingAuth ? (
          <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
        ) : isLoggedIn ? (
          <Button
            variant="ghost"
            size="sm"
            disabled={isLoggingOut}
            className="text-muted-foreground hover:text-destructive gap-2"
            onClick={handleSignOut}
          >
            {isLoggingOut ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <LogOut className="h-4 w-4" />
            )}
            {isLoggingOut ? "Signing Out..." : "Sign Out"}
          </Button>
        ) : (
          <Button asChild size="sm" className="gap-2">
            <Link href="/login">
              <LogIn className="h-4 w-4" />
              Login
            </Link>
          </Button>
        )}
      </div>
    </header>
  );
}
