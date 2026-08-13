const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export type QuoteResponse = {
  symbol: string;
  exchange: string;
  price: number | null;
  open: number | null;
  high: number | null;
  low: number | null;
  close: number | null;
  volume: number | null;
  timestamp: string | null;
  delayed: boolean;
  source: string;
  message?: string | null;
};

export type Candle = {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number | null;
};

export type HistoryResponse = {
  symbol: string;
  interval: string;
  source: string;
  delayed: boolean;
  candles: Candle[];
  message?: string | null;
};

export async function fetchQuote(symbol: string): Promise<QuoteResponse | null> {
  try {
    const response = await fetch(`${API_BASE}/api/v1/stocks/${symbol}/quote`, {
      next: { revalidate: 30 },
    });

    if (!response.ok) {
      return null;
    }

    return (await response.json()) as QuoteResponse;
  } catch {
    return null;
  }
}

export async function fetchHistory(symbol: string): Promise<HistoryResponse | null> {
  try {
    const response = await fetch(
      `${API_BASE}/api/v1/stocks/${symbol}/history?interval=1day&outputsize=120`,
      { next: { revalidate: 120 } },
    );

    if (!response.ok) {
      return null;
    }

    return (await response.json()) as HistoryResponse;
  } catch {
    return null;
  }
}
