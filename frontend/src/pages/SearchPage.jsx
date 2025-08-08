import { useState } from "react";
import { api } from "../api/client";
import { useQuery } from "@tanstack/react-query";

function CoachCard({ c }) {
  return (
    <div className="rounded-2xl shadow p-3 bg-white flex flex-col gap-2">
      <div className="aspect-video bg-gray-100 rounded-xl overflow-hidden">
        {c.photos?.[0] && <img src={c.photos[0]} alt={c.title} className="w-full h-full object-cover" loading="lazy" />}
      </div>
      <div className="font-semibold">{c.title || `${c.year || ""} ${c.model || ""}`}</div>
      <div className="text-sm text-gray-600">${c.price?.toLocaleString?.() || "—"}</div>
      <div className="text-xs text-gray-500">{c.location || ""}</div>
    </div>
  );
}

export default function SearchPage() {
  const [q, setQ] = useState("");
  const [sort, setSort] = useState("newest");
  const [minYear, setMinYear] = useState("");
  const [maxYear, setMaxYear] = useState("");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["search", q, sort, minYear, maxYear, minPrice, maxPrice],
    queryFn: async () => {
      try {
        const result = await api("/coaches/search", {
          q,
          sort,
          min_year: minYear || undefined,
          max_year: maxYear || undefined,
          min_price: minPrice || undefined,
          max_price: maxPrice || undefined,
          page: 1, 
          page_size: 24
        });
        console.log("API Response:", result);
        return result;
      } catch (err) {
        console.error("API Error:", err);
        throw err;
      }
    },
    retry: 1,
    refetchOnWindowFocus: false
  });

  // Debug logging
  if (error) {
    console.error("Query error:", error);
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto p-4 flex flex-col gap-4">
        <h1 className="text-3xl font-bold text-gray-900">PrevostGo - Luxury Coach Marketplace</h1>
        
        <div className="flex flex-col md:flex-row gap-3 bg-white p-4 rounded-lg shadow">
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && refetch()}
            placeholder="Search by year, model, converter..."
            className="flex-1 border rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <select 
            value={sort} 
            onChange={(e) => setSort(e.target.value)} 
            className="border rounded-xl px-3 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
            <option value="price_high">Price: High → Low</option>
            <option value="price_low">Price: Low → High</option>
          </select>
          <button 
            onClick={() => refetch()} 
            className="px-6 py-3 rounded-xl bg-blue-600 text-white hover:bg-blue-700 transition-colors font-medium"
            disabled={isLoading}
          >
            {isLoading ? "Searching..." : "Search"}
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            <p className="font-semibold">Error loading coaches</p>
            <p className="text-sm mt-1">{error.message || "Please check your connection and try again."}</p>
            <button 
              onClick={() => refetch()} 
              className="mt-2 text-sm underline hover:no-underline"
            >
              Retry
            </button>
          </div>
        )}

        {isLoading && (
          <div className="flex justify-center py-12">
            <div className="text-gray-600">Loading coaches...</div>
          </div>
        )}

        {data && data.length === 0 && (
          <div className="text-center py-12 text-gray-600">
            No coaches found. Try adjusting your search criteria.
          </div>
        )}

        {data && data.length > 0 && (
          <>
            <p className="text-gray-600">Found {data.length} coaches</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {data.map((c) => <CoachCard key={c.id} c={c} />)}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
