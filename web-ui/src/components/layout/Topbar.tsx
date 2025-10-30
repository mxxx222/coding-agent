"use client";
import React from "react";

export function Topbar() {
  return (
    <header className="md:hidden sticky top-0 z-10 bg-white border-b">
      <div className="h-14 px-4 flex items-center justify-between">
        <a href="/" className="font-semibold">Coding Agent</a>
        <a href="/secrets" className="text-sm underline">Menu</a>
      </div>
    </header>
  );
}


