"use client";
import React, { useState } from "react";

const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8002";
const adminToken = process.env.NEXT_PUBLIC_ADMIN_TOKEN;

export function SecretsImport() {
  const [passphrase, setPassphrase] = useState("");
  const [overwrite, setOverwrite] = useState(true);
  const [bundle, setBundle] = useState<any>(null);
  const [result, setResult] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function onFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        setBundle(JSON.parse(String(reader.result)));
      } catch (e) {
        setError("Invalid JSON bundle");
      }
    };
    reader.readAsText(file);
  }

  async function doImport(e: React.FormEvent) {
    e.preventDefault();
    if (!bundle) {
      setError("Select a bundle JSON file");
      return;
    }
    setError(null);
    setLoading(true);
    setResult("");
    try {
      const res = await fetch(`${apiBase}/api/secrets/import`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(adminToken ? { "X-Admin-Token": adminToken } : {}),
        },
        body: JSON.stringify({ bundle, passphrase, overwrite }),
      });
      const txt = await res.text();
      if (!res.ok) throw new Error(txt);
      setResult(txt);
    } catch (e: any) {
      setError(e?.message || "Import failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-3 border rounded p-4">
      <h3 className="font-semibold">Import Secrets</h3>
      {!adminToken && (
        <div className="text-sm text-yellow-700">Admin token missing in client env; import will be blocked.</div>
      )}
      {error && <div className="text-sm text-red-600">{error}</div>}
      <form onSubmit={doImport} className="space-y-3">
        <div>
          <label className="block text-sm">Bundle JSON</label>
          <input type="file" accept="application/json" onChange={onFile} className="mt-1" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label className="block text-sm">Passphrase</label>
            <input value={passphrase} onChange={(e) => setPassphrase(e.target.value)} className="mt-1 w-full border rounded px-2 py-1.5" />
          </div>
          <div className="flex items-end">
            <label className="inline-flex items-center gap-2">
              <input type="checkbox" checked={overwrite} onChange={(e) => setOverwrite(e.target.checked)} />
              Overwrite existing
            </label>
          </div>
        </div>
        <button disabled={loading || !adminToken} className="px-4 py-2 rounded bg-purple-600 text-white hover:bg-purple-700 disabled:opacity-50">
          {loading ? "Importing…" : "Import"}
        </button>
      </form>
      {!!result && (
        <pre className="bg-gray-50 border rounded p-3 text-sm whitespace-pre-wrap overflow-auto max-h-64">{result}</pre>
      )}
    </div>
  );
}


