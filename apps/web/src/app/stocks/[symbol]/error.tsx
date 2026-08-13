"use client";

export default function Error({ error }: { error: Error }) {
  return (
    <div className="rounded-xl border border-red-700/40 bg-red-950/20 p-4 text-red-200">
      Failed to load stock details: {error.message}
    </div>
  );
}
