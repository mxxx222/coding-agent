"use client";
import React, { useState } from "react";

const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8002";

export function CreateSecretForm({ onCreated }: { onCreated?: () => void }) {
  const [service, setService] = useState("openai");
  const [name, setName] = useState("");
  const [value, setValue] = useState("");
  const [rotation, setRotation] = useState("30_days");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${apiBase}/api/secrets`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, value, service, secret_type: "api_key", rotation_policy: rotation }),
      });
      if (!res.ok) throw new Error(await res.text());
      setName("");
      setValue("");
      if (onCreated) onCreated();
    } catch (e: any) {
      setError(e?.message || "Failed to create secret");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={submit} className="space-y-3 border rounded p-4">
      <h3 className="font-semibold">Create Secret</h3>
      {error && <div className="text-red-600 text-sm">{error}</div>}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div>
          <label className="block text-sm">Service</label>
          <input value={service} onChange={(e) => setService(e.target.value)} className="mt-1 w-full border rounded px-2 py-1.5" />
        </div>
        <div>
          <label className="block text-sm">Name</label>
          <input value={name} onChange={(e) => setName(e.target.value)} className="mt-1 w-full border rounded px-2 py-1.5" />
        </div>
        <div className="md:col-span-2">
          <label className="block text-sm">Value</label>
          <input value={value} onChange={(e) => setValue(e.target.value)} className="mt-1 w-full border rounded px-2 py-1.5" />
        </div>
        <div>
          <label className="block text-sm">Rotation</label>
          <select value={rotation} onChange={(e) => setRotation(e.target.value)} className="mt-1 w-full border rounded px-2 py-1.5">
            <option value="never">never</option>
            <option value="7_days">7_days</option>
            <option value="30_days">30_days</option>
            <option value="90_days">90_days</option>
          </select>
        </div>
      </div>
      <button disabled={loading} className="px-4 py-2 rounded bg-green-600 text-white hover:bg-green-700 disabled:opacity-50">
        {loading ? "Creating…" : "Create"}
      </button>
    </form>
  );
}


