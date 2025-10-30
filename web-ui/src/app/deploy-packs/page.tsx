import React from "react";
import { DeployPacks } from "@/components/DeployPacks";

export default function DeployPacksPage() {
  return (
    <main className="max-w-6xl mx-auto px-4 py-8 space-y-8">
      <h1 className="text-2xl font-bold">Deploy Packs</h1>
      <DeployPacks />
    </main>
  );
}


