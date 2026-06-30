"use client";

import { useState, useEffect } from "react";
import { AlertTriangle, X } from "lucide-react";

export default function FreeTierModal() {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const isDismissed = localStorage.getItem("dismiss-free-tier-modal");
    if (!isDismissed) {
      setIsOpen(true);
    }
  }, []);

  const handleClose = () => {
    setIsOpen(false);
    localStorage.setItem("dismiss-free-tier-modal", "true");
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm transition-all animate-in fade-in duration-200">
      <div className="relative w-full max-w-md bg-card border border-border rounded-xl shadow-2xl p-6 flex flex-col items-center text-center animate-in zoom-in-95 duration-200">
        <button
          onClick={handleClose}
          className="absolute top-4 right-4 text-muted-foreground hover:text-foreground p-1 hover:bg-secondary rounded-md transition-colors"
          aria-label="Close modal"
        >
          <X className="h-4 w-4" />
        </button>

        <div className="bg-amber-500/10 p-3 rounded-full text-amber-500 mb-4">
          <AlertTriangle className="h-6 w-6" />
        </div>

        <h3 className="text-lg font-semibold tracking-tight mb-2">
          Notice: Free Tier Service
        </h3>

        <p className="text-sm text-muted-foreground leading-relaxed mb-6">
          This project is built using free-tier tools and hosting services. As a
          result, AI responses might experience delays or be less accurate at
          times. Thank you for your understanding and patience!
        </p>

        <button
          onClick={handleClose}
          className="w-full bg-primary text-primary-foreground hover:bg-primary/90 font-medium text-sm py-2.5 px-4 rounded-lg transition-colors shadow-sm"
        >
          I Understand
        </button>
      </div>
    </div>
  );
}
