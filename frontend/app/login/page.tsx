"use client";

import Link from "next/link";
import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import {
  Sparkles,
  Loader2,
  Eye,
  EyeOff,
  AlertCircle,
  CheckCircle2,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { apiClient } from "@/lib/api-client";

function LoginContent() {
  const searchParams = useSearchParams();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSuccess, setShowSuccess] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    if (searchParams.get("registered") === "true") {
      setShowSuccess(true);
    }
  }, [searchParams]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setShowSuccess(false);

    const form = e.currentTarget;
    const username = (form.elements.namedItem("username") as HTMLInputElement)
      .value;
    const password = (form.elements.namedItem("password") as HTMLInputElement)
      .value;

    try {
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);

      await apiClient.post("/login", formData.toString(), {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      localStorage.setItem("user_logged_in", "true");
      location.reload();
    } catch (err: any) {
      const serverErrorMessage =
        err.response?.data?.detail || err.response?.data?.message;
      setError(serverErrorMessage || "Something went wrong. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="relative flex min-h-screen items-center justify-center bg-background px-4 overflow-hidden">
      <div className="absolute inset-0 -z-10 bg-[radial-gradient(ellipse_at_top,var(--tw-gradient-stops))] from-primary/10 via-background to-background" />
      <div className="absolute inset-0 -z-10 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-size-[14px_24px]" />

      <Card className="w-full max-w-md border-muted/50 bg-card/60 backdrop-blur-md shadow-xl transition-all duration-300 hover:shadow-2xl hover:border-primary/20 animate-in fade-in slide-in-from-bottom-4">
        <CardHeader className="text-center space-y-4 pt-8">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 shadow-inner relative group transition-transform duration-300 hover:scale-105">
            <Sparkles className="h-7 w-7 text-primary animate-pulse" />
            <div className="absolute inset-0 rounded-2xl bg-primary/20 blur-md opacity-0 group-hover:opacity-100 transition-opacity duration-300 -z-10" />
          </div>

          <div className="space-y-1.5">
            <h1 className="text-2xl font-bold tracking-tight bg-linear-to-r from-foreground to-foreground/80 bg-clip-text">
              Welcome back
            </h1>
            <p className="text-sm text-muted-foreground">
              Sign in to continue to{" "}
              <span className="font-medium text-foreground">AI Assistant</span>
            </p>
          </div>
        </CardHeader>

        <CardContent className="space-y-6 pb-8">
          {showSuccess && (
            <div className="flex items-center gap-2.5 p-3.5 text-sm text-emerald-600 bg-emerald-50 dark:bg-emerald-950/20 dark:text-emerald-400 border border-emerald-200/50 dark:border-emerald-900/30 rounded-xl font-medium animate-in fade-in duration-300">
              <CheckCircle2 className="h-5 w-5 shrink-0" />
              <span>Account created successfully! Please sign in.</span>
            </div>
          )}

          {error && (
            <div className="flex items-center gap-2.5 p-3.5 text-sm text-destructive bg-destructive/5 border border-destructive/10 rounded-xl font-medium animate-in fade-in duration-300">
              <AlertCircle className="h-5 w-5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form className="space-y-4" onSubmit={handleSubmit}>
            <div className="space-y-2">
              <Label
                htmlFor="username"
                className="text-xs font-semibold tracking-wide text-muted-foreground uppercase"
              >
                Email / Username
              </Label>
              <Input
                id="username"
                name="username"
                type="text"
                placeholder="johndoe"
                required
                disabled={isLoading}
                className="h-11 bg-background/50 border-muted-foreground/20 focus-visible:ring-primary/40 transition-all rounded-xl"
              />
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <Label
                  htmlFor="password"
                  className="text-xs font-semibold tracking-wide text-muted-foreground uppercase"
                >
                  Password
                </Label>
                <Link
                  href="#"
                  className="text-xs text-primary/80 hover:text-primary hover:underline transition-colors"
                >
                  Forgot password?
                </Link>
              </div>
              <div className="relative">
                <Input
                  id="password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="••••••••"
                  required
                  disabled={isLoading}
                  className="h-11 bg-background/50 border-muted-foreground/20 focus-visible:ring-primary/40 transition-all rounded-xl pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>

            <Button
              className="w-full h-11 text-sm font-medium shadow-md shadow-primary/10 transition-all duration-300 active:scale-[0.98] rounded-xl mt-2"
              type="submit"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                "Sign in"
              )}
            </Button>
          </form>

          <div className="relative flex py-2 items-center">
            <div className="grow border-t border-muted" />
            <span className="shrink mx-4 text-xs text-muted-foreground/60 uppercase tracking-wider">
              or
            </span>
            <div className="grow border-t border-muted" />
          </div>

          <p className="text-center text-sm text-muted-foreground">
            Don&apos;t have an account?{" "}
            <Link
              href="/register"
              className="text-primary font-medium hover:underline underline-offset-4 transition-all"
            >
              Sign up
            </Link>
          </p>
        </CardContent>
      </Card>
    </main>
  );
}

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center bg-background">
          <div className="relative flex items-center justify-center">
            <div className="h-12 w-12 rounded-full border-4 border-primary/20 border-t-primary animate-spin" />
          </div>
        </div>
      }
    >
      <LoginContent />
    </Suspense>
  );
}
