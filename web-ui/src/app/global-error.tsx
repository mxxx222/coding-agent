"use client";
import React from "react";

export default function GlobalError({ error, reset }: { error: Error & { digest?: string }, reset: () => void }) {
  return (
    <html>
      <body>
        <main className="max-w-2xl mx-auto px-4 py-16">
          <h1 className="text-2xl font-bold mb-2">App crashed</h1>
          <p className="text-gray-600 mb-6">A global error occurred. You can try to recover.</p>
          <div className="space-x-2">
            <button onClick={() => reset()} className="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700">Reload app</button>
            <a href="/" className="px-4 py-2 rounded bg-gray-100 hover:bg-gray-200">Go home</a>
          </div>
        </main>
      </body>
    </html>
  );
}


