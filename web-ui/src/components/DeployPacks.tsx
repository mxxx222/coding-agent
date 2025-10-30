"use client";
import React from "react";

export function DeployPacks() {
  const packs = [
    {
      id: "nextjs-supabase-stripe",
      title: "Next.js + Supabase + Stripe",
      desc: "Web app with auth, database and payments.",
      href: "/auto-deploy",
    },
    {
      id: "fastapi-prefect-ml",
      title: "FastAPI + Prefect + pgvector",
      desc: "ML/ops starter with workflows and embeddings.",
      href: "/auto-deploy",
    },
  ];
  return (
    <div className="space-y-3">
      <h2 className="text-xl font-semibold">Deploy Packs</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {packs.map((p) => (
          <a key={p.id} href={p.href} className="card p-4 hover:shadow transition">
            <div className="font-medium mb-1">{p.title}</div>
            <div className="text-sm text-gray-600">{p.desc}</div>
          </a>
        ))}
      </div>
    </div>
  );
}


