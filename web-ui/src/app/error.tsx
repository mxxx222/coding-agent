"use client";
import React, { useEffect } from "react";

export default function Error({ error, reset }: { error: Error & { digest?: string }, reset: () => void }) {
  useEffect(() => {
    // eslint-disable-next-line no-console
    console.error("Route error:", error);
  }, [error]);

  return (
    <main className="max-w-2xl mx-auto px-4 py-16">
      <h1 className="text-2xl font-bold mb-2">Something went wrong</h1>
      <p className="text-gray-600 mb-6">An error occurred while rendering this page.</p>
      <div className="space-x-2">
        <button onClick={() => reset()} className="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700">Try again</button>
        <a href="/" className="px-4 py-2 rounded bg-gray-100 hover:bg-gray-200">Go home</a>
      </div>
    </main>
  );
}


