import React from "react";

export default function NotFound() {
  return (
    <main className="max-w-2xl mx-auto px-4 py-16">
      <h1 className="text-2xl font-bold mb-2">Not Found</h1>
      <p className="text-gray-600 mb-6">The page you requested could not be found.</p>
      <a href="/" className="px-4 py-2 rounded bg-gray-100 hover:bg-gray-200">Go home</a>
    </main>
  );
}


