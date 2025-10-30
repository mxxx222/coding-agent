"use client";
import React from "react";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Home" },
  { href: "/auto-deploy", label: "Auto‑Deploy" },
  { href: "/secrets", label: "Secrets" },
  { href: "/secrets/providers", label: "Providers" },
  { href: "/secrets/tools", label: "Tools" },
];

export function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="hidden md:block md:w-64 h-full border-r bg-white">
      <div className="h-14 border-b px-4 flex items-center font-semibold">Coding Agent</div>
      <nav className="p-2 space-y-1">
        {links.map((l) => {
          const active = pathname === l.href;
          return (
            <a
              key={l.href}
              href={l.href}
              className={`block px-3 py-2 rounded text-sm hover:bg-gray-100 ${active ? "bg-gray-100 font-medium" : "text-gray-700"}`}
            >
              {l.label}
            </a>
          );
        })}
      </nav>
    </aside>
  );
}


