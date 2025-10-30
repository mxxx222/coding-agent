"use client";
import React, { useEffect, useState } from "react";

type SecretMeta = {
  id: string;
  name: string;
  service: string;
  secret_type: string;
  created_at?: string;
  expires_at?: string | null;
  last_rotated?: string | null;
  usage_count?: number;
};

const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8002";

export function SecretsList() {
  const [items, setItems] = useState<SecretMeta[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${apiBase}/api/secrets`);
      const json = await res.json();
      setItems(json.secrets || []);
    } catch (e: any) {
      setError(e?.message || "Failed to load secrets");
    } finally {
      setLoading(false);
    }
  }

  async function rotate(id: string) {
    await fetch(`${apiBase}/api/secrets/${id}/rotate`, { method: "POST" });
    await load();
  }

  async function del(id: string) {
    await fetch(`${apiBase}/api/secrets/${id}`, { method: "DELETE" });
    await load();
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Secrets</h2>
        <button
          onClick={load}
          className="px-3 py-1.5 rounded bg-gray-100 hover:bg-gray-200"
        >
          Refresh
        </button>
      </div>
      {loading && <div>Loading…</div>}
      {error && <div className="text-red-600">{error}</div>}
      <div className="border rounded divide-y">
        {items.map((s) => (
          <div key={s.id} className="p-3 flex items-center justify-between">
            <div>
              <div className="font-medium">{s.service}/{s.name}</div>
              <div className="text-sm text-gray-500">
                type: {s.secret_type} • uses: {s.usage_count ?? 0}
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => rotate(s.id)}
                className="px-3 py-1.5 rounded bg-blue-600 text-white hover:bg-blue-700"
              >
                Rotate
              </button>
              <button
                onClick={() => del(s.id)}
                className="px-3 py-1.5 rounded bg-red-600 text-white hover:bg-red-700"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
        {items.length === 0 && !loading && (
          <div className="p-3 text-gray-500">No secrets yet.</div>
        )}
      </div>
    </div>
  );
}


