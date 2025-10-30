"use client";
import React, { useState } from "react";

const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8002";
const adminToken = process.env.NEXT_PUBLIC_ADMIN_TOKEN;

type Provider = "vault" | "aws" | "gcp";

export function ProvidersConfig() {
  const [provider, setProvider] = useState<Provider>("vault");
  const [prefix, setPrefix] = useState("coding-agent");
  const [config, setConfig] = useState<any>({});
  const [result, setResult] = useState<string>("");

  function setField(key: string, value: string) {
    setConfig((c: any) => ({ ...c, [key]: value }));
  }

  async function test() {
    setResult("");
    const res = await fetch(`${apiBase}/api/secrets/providers/test`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(adminToken ? { "X-Admin-Token": adminToken } : {}),
      },
      body: JSON.stringify({ provider, config }),
    });
    setResult(await res.text());
  }

  async function sync(action: "push" | "pull") {
    setResult("");
    const res = await fetch(`${apiBase}/api/secrets/sync`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(adminToken ? { "X-Admin-Token": adminToken } : {}),
      },
      body: JSON.stringify({ provider, action, prefix }),
    });
    setResult(await res.text());
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Providers</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div>
          <label className="block text-sm">Provider</label>
          <select value={provider} onChange={(e) => setProvider(e.target.value as Provider)} className="mt-1 w-full border rounded px-2 py-1.5">
            <option value="vault">Vault</option>
            <option value="aws">AWS Secrets Manager</option>
            <option value="gcp">GCP Secret Manager</option>
          </select>
        </div>
        <div>
          <label className="block text-sm">Prefix</label>
          <input value={prefix} onChange={(e) => setPrefix(e.target.value)} className="mt-1 w-full border rounded px-2 py-1.5" />
        </div>
      </div>

      {/* Dynamic fields */}
      {provider === "vault" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label className="block text-sm">Address (VAULT_ADDR)</label>
            <input onChange={(e) => setField("address", e.target.value)} className="mt-1 w-full border rounded px-2 py-1.5" />
          </div>
          <div>
            <label className="block text-sm">Token (VAULT_TOKEN)</label>
            <input onChange={(e) => setField("token", e.target.value)} className="mt-1 w-full border rounded px-2 py-1.5" />
          </div>
          <div>
            <label className="block text-sm">Mount (default secret)</label>
            <input onChange={(e) => setField("mount", e.target.value)} className="mt-1 w-full border rounded px-2 py-1.5" />
          </div>
        </div>
      )}

      {provider === "aws" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label className="block text-sm">Region (AWS_REGION)</label>
            <input onChange={(e) => setField("region", e.target.value)} className="mt-1 w-full border rounded px-2 py-1.5" />
          </div>
        </div>
      )}

      {provider === "gcp" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label className="block text-sm">Project (GCP_PROJECT)</label>
            <input onChange={(e) => setField("project", e.target.value)} className="mt-1 w-full border rounded px-2 py-1.5" />
          </div>
        </div>
      )}

      <div className="flex items-center gap-2">
        <button onClick={test} className="px-3 py-1.5 rounded bg-gray-100 hover:bg-gray-200">Test</button>
        <button onClick={() => sync("push")} className="px-3 py-1.5 rounded bg-blue-600 text-white hover:bg-blue-700">Push</button>
        <button onClick={() => sync("pull")} className="px-3 py-1.5 rounded bg-purple-600 text-white hover:bg-purple-700">Pull</button>
      </div>

      {!!result && (
        <pre className="bg-gray-50 border rounded p-3 text-sm whitespace-pre-wrap">{result}</pre>
      )}
    </div>
  );
}


