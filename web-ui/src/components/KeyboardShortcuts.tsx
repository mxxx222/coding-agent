"use client";
import React from "react";
import { useRouter } from "next/navigation";

export function KeyboardShortcuts() {
  const router = useRouter();

  React.useEffect(() => {
    let buffer: string[] = [];
    const onKey = (e: KeyboardEvent) => {
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      const key = e.key.toLowerCase();
      buffer.push(key);
      if (buffer.length > 2) buffer.shift();
      const seq = buffer.join(" ");
      // g h -> home
      if (seq === "g h") router.push("/");
      // g s -> secrets
      if (seq === "g s") router.push("/secrets");
      // g p -> providers
      if (seq === "g p") router.push("/secrets/providers");
      // g t -> tools
      if (seq === "g t") router.push("/secrets/tools");
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [router]);

  return null;
}


