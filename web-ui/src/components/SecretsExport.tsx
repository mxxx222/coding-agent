"use client";
import React, { useState } from "react";

const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8002";
const adminToken = process.env.NEXT_PUBLIC_ADMIN_TOKEN;

export function SecretsExport() {
  const [passphrase, setPassphrase] = useState("");
  const [services, setServices] = useState("");
  const [bundle, setBundle] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function doExport(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const include_services = services
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      const res = await fetch(`${apiBase}/api/secrets/export`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(adminToken ? { "X-Admin-Token": adminToken } : {}),
        },
        body: JSON.stringify({ passphrase, include_services: include_services.length ? include_services : undefined }),
      });
      if (!res.ok) throw new Error(await res.text());
      const json = await res.json();
      setBundle(json.bundle);
    } catch (e: any) {
      setError(e?.message || "Export failed");
    } finally {
      setLoading(false);
    }
  }

  function download() {
    if (!bundle) return;
    const blob = new Blob([JSON.stringify(bundle, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "secrets.bundle.json";
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="space-y-3 border rounded p-4">
      <h3 className="font-semibold">Export Secrets</h3>
      {!adminToken && (
        <div className="text-sm text-yellow-700">Admin token missing in client env; export will likely be blocked.</div>
      )}
      {error && <div className="text-sm text-red-600">{error}</div>}
      <form onSubmit={doExport} className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div>
          <label className="block text-sm">Passphrase</label>
          <input value={passphrase} onChange={(e) => setPassphrase(e.target.value)} className="mt-1 w-full border rounded px-2 py-1.5" />
        </div>
        <div>
          <label className="block text-sm">Include services (comma-separated)</label>
          <input value={services} onChange={(e) => setServices(e.target.value)} className="mt-1 w-full border rounded px-2 py-1.5" />
        </div>
        <div className="md:col-span-2">
          <button disabled={loading} className="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50">
            {loading ? "Exporting…" : "Export"}
          </button>
        </div>
      </form>
      {bundle && (
        <div className="space-y-2">
          <button onClick={download} className="px-3 py-1.5 rounded bg-gray-100 hover:bg-gray-200">Download bundle</button>
          <pre className="bg-gray-50 border rounded p-3 text-sm whitespace-pre-wrap overflow-auto max-h-64">{JSON.stringify(bundle, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}


