"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    const newChatId = crypto.randomUUID();
    router.replace(`/chat/${newChatId}`);
  }, [router]);

  return <></>;
}
