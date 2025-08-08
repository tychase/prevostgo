import { useEffect, useMemo, useState } from "react";

export default function SearchBar({ onSearch }) {
  const [mode, setMode] = useState("buy");
  const [filters, setFilters] = useState({
    query: "",
    condition: "used",
  });

  // Debounced auto-search
  useEffect(() => {
    const t = setTimeout(() => onSearch({ mode, filters }), 350);
    return () => clearTimeout(t);
  }, [mode, filters]);

  const placeholder = useMemo(
    () =>
      mode === "buy"
        ? "Search make, model, converter…"
        : "Describe your coach to sell/trade",
    [mode]
  );

  return (
    <div className="w-full max-w-5xl mx-auto">
      {/* Tabs */}
      <div className="flex gap-2 mb-3">
        <button
          className={`px-4 py-2 rounded-xl ${mode === "buy" ? "bg-white text-black" : "bg-slate-700"}`}
          onClick={() => setMode("buy")}
        >
          Buy
        </button>
        <button
          className={`px-4 py-2 rounded-xl ${mode === "sell" ? "bg-white text-black" : "bg-slate-700"}`}
          onClick={() => setMode("sell")}
        >
          Sell/Trade
        </button>
      </div>

      {/* Input row */}
      <div className="flex gap-2 items-center">
        <select
          value={filters.condition}
          onChange={(e) =>
            setFilters((f) => ({ ...f, condition: e.target.value }))
          }
          className="px-3 py-2 rounded-lg bg-slate-800"
        >
          <option value="used">Used</option>
          <option value="new">New</option>
        </select>

        <input
          value={filters.query}
          onChange={(e) => setFilters((f) => ({ ...f, query: e.target.value }))}
          placeholder={placeholder}
          className="flex-1 px-4 py-2 rounded-lg bg-slate-800"
          onKeyDown={(e) => {
            if (e.key === "Enter") onSearch({ mode, filters });
          }}
        />
      </div>

      {/* Sticky Search button */}
      <div className="fixed bottom-6 left-0 right-0 flex justify-center pointer-events-none z-50">
        <button
          className="pointer-events-auto px-6 py-3 rounded-full shadow-lg bg-indigo-600 font-semibold"
          onClick={() => onSearch({ mode, filters })}
        >
          Search
        </button>
      </div>
    </div>
  );
}