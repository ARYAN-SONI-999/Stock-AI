import Link from "next/link";

import { QuoteCard } from "@/components/quote-card";
import { fetchQuote } from "@/lib/api";

const spotlightSymbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"];

export default async function Home() {
  const [relianceQuote] = await Promise.all([fetchQuote("RELIANCE")]);

  return (
    <main className="space-y-8">
      <section className="rounded-2xl border border-zinc-800 bg-zinc-900/40 p-6">
        <h1 className="text-3xl font-bold">StockMind AI</h1>
        <p className="mt-3 max-w-3xl text-sm text-zinc-300">
          Decision-support platform for Indian equities with transparent uncertainty, leakage-aware modeling, and explicit delayed-data signaling.
        </p>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <QuoteCard quote={relianceQuote} />
        <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-4">
          <h2 className="text-lg font-semibold">Stock Universe (Phase 1-3 baseline)</h2>
          <p className="mt-2 text-sm text-zinc-300">
            Instrument master ingestion is scaffolded in the backend. Search and details will expand as exchange master files are ingested.
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            {spotlightSymbols.map((symbol) => (
              <Link
                key={symbol}
                href={`/stocks/${symbol}`}
                className="rounded-md border border-zinc-700 px-3 py-1 text-xs text-zinc-200 hover:border-zinc-500"
              >
                {symbol}
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="rounded-xl border border-zinc-800 bg-zinc-950 p-4">
        <h2 className="text-lg font-semibold">Safety & Transparency</h2>
        <ul className="mt-3 list-disc space-y-1 pl-6 text-sm text-zinc-300">
          <li>Predictions are probabilistic and never guaranteed.</li>
          <li>Historical performance is separated from future uncertainty.</li>
          <li>No fabricated live data. Delays/unavailability are explicitly shown.</li>
          <li>Model performance must be measured via out-of-sample validation.</li>
        </ul>
      </section>
    </main>
  );
}
