"use client";

import { MoreVertical, Trash2, MessageSquare } from "lucide-react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ConfirmModal } from "@/components/ui/confirm-modal";

interface SidebarChatItemProps {
  sessionId: string;
  title: string;
  isActive: boolean;
  isDeleting: boolean;
  onDelete: (id: string) => Promise<void>;
}

export function SidebarChatItem({
  sessionId,
  title,
  isActive,
  isDeleting,
  onDelete,
}: SidebarChatItemProps) {
  const router = useRouter();

  return (
    <div className="group relative flex items-center w-66 rounded-lg overflow-hidden transition-all duration-200">
      <Button
        variant={isActive ? "secondary" : "ghost"}
        className={`w-full justify-start gap-2.5 text-left relative h-9.5 rounded-lg group/btn transition-colors overflow-hidden ${
          isActive
            ? "bg-secondary font-medium text-foreground"
            : "text-muted-foreground hover:text-foreground hover:bg-muted/60"
        }`}
        onClick={() => router.push(`/chat/${sessionId}`)}
        disabled={isDeleting}
      >
        <MessageSquare
          className={`h-4 w-4 shrink-0 transition-colors ${
            isActive
              ? "text-primary"
              : "text-muted-foreground/60 group-hover/btn:text-muted-foreground"
          }`}
        />

        <span className="truncate flex-1 block text-start min-w-0 text-sm [direction:auto]">
          {isDeleting ? "Deleting..." : title || "Untitled Chat"}
        </span>
      </Button>

      <div className="absolute right-2 opacity-0 group-hover:opacity-100 transition-all duration-200 z-10 shrink-0 transform scale-95 group-hover:scale-100">
        <ConfirmModal
          title="Delete Chat"
          description="Are you sure you want to delete this chat session and all associated conversation history? This action cannot be undone."
          confirmText="Delete Chat"
          variant="destructive"
          onConfirm={() => onDelete(sessionId)}
        >
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                className="h-7 w-7 p-0 rounded-md hover:bg-foreground/10 text-muted-foreground hover:text-foreground cursor-pointer transition-colors"
                onClick={(e) => e.stopPropagation()}
              >
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              align="end"
              className="w-36 shadow-md rounded-lg"
            >
              <DropdownMenuItem
                className="text-destructive focus:text-destructive gap-2 cursor-pointer select-none py-1.5"
                onClick={(e) => e.stopPropagation()}
              >
                <Trash2 className="h-4 w-4" />
                <span className="text-xs font-medium">Delete</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </ConfirmModal>
      </div>
    </div>
  );
}
