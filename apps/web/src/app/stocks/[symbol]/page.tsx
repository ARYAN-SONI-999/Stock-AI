import { CandlesChart } from "@/components/candles-chart";
import { QuoteCard } from "@/components/quote-card";
import { fetchHistory, fetchQuote } from "@/lib/api";

export default async function StockDetailsPage({
  params,
}: {
  params: Promise<{ symbol: string }>;
}) {
  const { symbol } = await params;
  const normalized = symbol.toUpperCase();

  const [quote, history] = await Promise.all([fetchQuote(normalized), fetchHistory(normalized)]);

  return (
    <main className="space-y-6">
      <header className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-4">
        <h1 className="text-2xl font-bold">{normalized}</h1>
        <p className="mt-1 text-sm text-zinc-300">
          Stock details, technical overview, and explainable intelligence scaffold.
        </p>
      </header>

      <QuoteCard quote={quote} />

      <section className="rounded-xl border border-zinc-800 bg-zinc-950 p-4">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Interactive Candlestick Chart</h2>
          <span className="text-xs text-zinc-400">Timeframe: 1D (Phase 1 baseline)</span>
        </div>

        {history && history.candles.length > 0 ? (
          <CandlesChart candles={history.candles} />
        ) : (
          <div className="rounded-md border border-amber-700/40 bg-amber-950/20 p-3 text-sm text-amber-200">
            {history?.message ?? "Data delayed / unavailable."}
          </div>
        )}
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-4">
          <h3 className="font-semibold">Technical Analysis</h3>
          <p className="mt-2 text-sm text-zinc-300">Indicator engine and score breakdown are available at `/api/v1/stocks/{symbol}/technical`.</p>
        </div>
        <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-4">
          <h3 className="font-semibold">Prediction Policy</h3>
          <p className="mt-2 text-sm text-zinc-300">This platform only serves probabilistic forecasts with uncertainty ranges and explicit limitations.</p>
        </div>
      </section>
    </main>
  );
}
