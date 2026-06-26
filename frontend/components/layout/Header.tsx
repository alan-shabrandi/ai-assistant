"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Sparkles, LogOut, LogIn, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";

export default function Header() {
  const router = useRouter();
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
  const [checkingAuth, setCheckingAuth] = useState<boolean>(true);

  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        const userLoggedFlag = localStorage.getItem("user_logged_in");
        setIsLoggedIn(userLoggedFlag === "true");
      } catch (err) {
        setIsLoggedIn(false);
      } finally {
        setCheckingAuth(false);
      }
    };

    checkAuthStatus();
  }, []);

  const handleSignOut = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/logout`,
        {
          method: "POST",
          credentials: "include",
        },
      );

      if (response.ok) {
        localStorage.removeItem("user_logged_in");
        setIsLoggedIn(false);
        router.push("/login");
        router.refresh();
      }
    } catch (error) {
      console.error("Logout failed:", error);
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
            className="text-muted-foreground hover:text-destructive gap-2"
            onClick={handleSignOut}
          >
            <LogOut className="h-4 w-4" />
            Sign Out
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
