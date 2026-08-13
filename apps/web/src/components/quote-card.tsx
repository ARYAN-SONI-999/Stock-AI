import { QuoteResponse } from "@/lib/api";

function formatPrice(value: number | null): string {
  if (value === null || Number.isNaN(value)) {
    return "—";
  }
  return `₹${value.toLocaleString("en-IN", { maximumFractionDigits: 2 })}`;
}

export function QuoteCard({ quote }: { quote: QuoteResponse | null }) {
  if (!quote) {
    return (
      <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-4 text-sm text-zinc-300">
        Quote unavailable.
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">
          {quote.symbol} · {quote.exchange}
        </h3>
        <span className={`text-xs ${quote.delayed ? "text-amber-300" : "text-emerald-300"}`}>
          {quote.delayed ? "Data delayed / unavailable" : "Live/Near-live"}
        </span>
      </div>
      <p className="mt-3 text-3xl font-bold text-white">{formatPrice(quote.price)}</p>
      <p className="mt-2 text-xs text-zinc-400">
        Timestamp: {quote.timestamp ? new Date(quote.timestamp).toLocaleString("en-IN", { timeZone: "Asia/Kolkata" }) : "N/A"} IST
      </p>
      {quote.message ? <p className="mt-2 text-xs text-amber-300">{quote.message}</p> : null}
    </div>
  );
}
