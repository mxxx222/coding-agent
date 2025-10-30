"use client";
import React from "react";
import { ThemeToggle } from "@/components/ui/ThemeToggle";

export function Topbar() {
  return (
    <header className="md:hidden sticky top-0 z-10 bg-white border-b">
      <div className="h-14 px-4 flex items-center justify-between">
        <a href="/" className="font-semibold">Coding Agent</a>
        <div className="flex items-center gap-3">
          <ThemeToggle />
          <a href="/secrets" className="text-sm underline">Menu</a>
        </div>
      </div>
    </header>
  );
}


