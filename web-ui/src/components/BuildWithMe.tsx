"use client";
import React from "react";

const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8002";

type Step = 1 | 2 | 3 | 4 | 5;

export function BuildWithMe() {
  const [step, setStep] = React.useState<Step>(1);
  const [providerHealthy, setProviderHealthy] = React.useState<{vault?: boolean; aws?: boolean; gcp?: boolean}>({});
  const [status, setStatus] = React.useState<string>("");

  async function testProviders() {
    setStatus("Testing providers...");
    const providers = ["vault","aws","gcp"] as const;
    const out: any = {};
    for (const p of providers) {
      try {
        const res = await fetch(`${apiBase}/api/secrets/providers/test`, {
          method: "POST",
          headers: {"Content-Type":"application/json"},
          body: JSON.stringify({provider: p, config: {}}),
        });
        const json = await res.json();
        out[p] = !!json.healthy;
      } catch { out[p] = false; }
    }
    setProviderHealthy(out);
    setStatus("Providers tested");
  }

  function next() { setStep((s) => Math.min(5, (s + 1) as Step)); }
  function prev() { setStep((s) => Math.max(1, (s - 1) as Step)); }

  return (
    <div className="space-y-6">
      <div className="card p-4">
        <h2 className="text-xl font-semibold mb-2">Build with me</h2>
        <p className="text-sm text-gray-600">Guided setup: pick a pack, check secrets, test providers, deploy.</p>
      </div>

      <div className="card p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="text-sm">Step {step} / 5</div>
          <div className="flex gap-2">
            {step > 1 && <button onClick={prev} className="px-3 py-1.5 rounded bg-gray-100 hover:bg-gray-200">Back</button>}
            {step < 5 && <button onClick={next} className="px-3 py-1.5 rounded bg-blue-600 text-white hover:bg-blue-700">Next</button>}
          </div>
        </div>

        {step === 1 && (
          <div className="space-y-2">
            <h3 className="font-semibold">Choose a Deploy Pack</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <a href="/deploy-packs" className="card p-4 hover:shadow transition">
                <div className="font-medium mb-1">Next.js + Supabase + Stripe</div>
                <div className="text-sm text-gray-600">Web app with auth, data, and payments.</div>
              </a>
              <a href="/deploy-packs" className="card p-4 hover:shadow transition">
                <div className="font-medium mb-1">FastAPI + Prefect + pgvector</div>
                <div className="text-sm text-gray-600">ML/ops starter with workflows and embeddings.</div>
              </a>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-3">
            <h3 className="font-semibold">Add required secrets</h3>
            <p className="text-sm text-gray-600">Open the Secrets page to add API keys (OpenAI, Vercel, Notion, etc.).</p>
            <a href="/secrets" className="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 inline-block w-max">Open Secrets</a>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-3">
            <h3 className="font-semibold">Test provider connectivity</h3>
            <div className="flex items-center gap-2">
              <button onClick={testProviders} className="px-4 py-2 rounded bg-gray-100 hover:bg-gray-200">Run tests</button>
              {status && <div className="text-sm text-gray-600">{status}</div>}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {(["vault","aws","gcp"] as const).map(p => (
                <div key={p} className={`p-3 rounded border ${providerHealthy[p] ? 'border-green-400 bg-green-50' : 'border-gray-200 bg-white'}`}>
                  <div className="font-medium">{p.toUpperCase()}</div>
                  <div className="text-sm">{providerHealthy[p] ? 'Healthy' : 'Unknown'}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {step === 4 && (
          <div className="space-y-3">
            <h3 className="font-semibold">Configure Deploy Pack</h3>
            <p className="text-sm text-gray-600">Use provider presets or defaults. You can refine later.</p>
            <a href="/secrets/providers" className="px-4 py-2 rounded bg-gray-100 hover:bg-gray-200 inline-block w-max">Open Providers</a>
          </div>
        )}

        {step === 5 && (
          <div className="space-y-3">
            <h3 className="font-semibold">Deploy</h3>
            <p className="text-sm text-gray-600">Run the Notion → Deploy pipeline and monitor status.</p>
            <a href="/auto-deploy" className="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 inline-block w-max">Open Auto‑Deploy</a>
          </div>
        )}
      </div>
    </div>
  );
}


