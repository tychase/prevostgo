import { useState } from "react";
import { api } from "../api/client";
import { useQuery } from "@tanstack/react-query";

function CoachCard({ c }) {
  return (
    <div className="rounded-lg overflow-hidden shadow-lg bg-gray-900 border border-gray-800 hover:border-orange-500 transition-all duration-300">
      <div className="aspect-video bg-gray-800 relative">
        {c.photos?.[0] && (
          <img src={c.photos[0]} alt={c.title} className="w-full h-full object-cover" loading="lazy" />
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
      </div>
      <div className="p-4">
        <div className="font-bold text-white text-lg">{c.title || `${c.year || ""} ${c.model || ""}`}</div>
        <div className="text-orange-500 font-semibold text-xl mt-1">
          ${c.price?.toLocaleString?.() || "Contact for Price"}
        </div>
        <div className="text-gray-400 text-sm mt-2">{c.location || "Location TBD"}</div>
      </div>
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

  return (
    <div className="min-h-screen bg-black">
      {/* Hero Section */}
      <div className="bg-gradient-to-b from-gray-900 to-black py-12">
        <div className="max-w-7xl mx-auto px-4">
          <h1 className="text-5xl font-bold text-white mb-4">
            PrevostGo
          </h1>
          <p className="text-xl text-orange-500 font-semibold">
            Luxury Coach Marketplace
          </p>
        </div>
      </div>

      {/* Search Section */}
      <div className="max-w-7xl mx-auto px-4 -mt-8">
        <div className="bg-gray-900 rounded-lg shadow-2xl p-6 border border-gray-800">
          <div className="flex flex-col lg:flex-row gap-4">
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && refetch()}
              placeholder="Search by year, model, converter..."
              className="flex-1 bg-black border border-gray-700 text-white rounded-lg px-6 py-4 focus:outline-none focus:border-orange-500 transition-colors placeholder-gray-500"
            />
            <select 
              value={sort} 
              onChange={(e) => setSort(e.target.value)} 
              className="bg-black border border-gray-700 text-white rounded-lg px-6 py-4 focus:outline-none focus:border-orange-500 transition-colors"
            >
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
              <option value="price_high">Price: High → Low</option>
              <option value="price_low">Price: Low → High</option>
            </select>
            <button 
              onClick={() => refetch()} 
              className="px-8 py-4 rounded-lg bg-orange-500 text-black font-bold hover:bg-orange-400 transition-all duration-300 shadow-lg hover:shadow-orange-500/25"
              disabled={isLoading}
            >
              {isLoading ? "Searching..." : "Search"}
            </button>
          </div>

          {/* Advanced Filters */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
            <input
              type="number"
              value={minYear}
              onChange={(e) => setMinYear(e.target.value)}
              placeholder="Min Year"
              className="bg-black border border-gray-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:border-orange-500 transition-colors placeholder-gray-500"
            />
            <input
              type="number"
              value={maxYear}
              onChange={(e) => setMaxYear(e.target.value)}
              placeholder="Max Year"
              className="bg-black border border-gray-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:border-orange-500 transition-colors placeholder-gray-500"
            />
            <input
              type="number"
              value={minPrice}
              onChange={(e) => setMinPrice(e.target.value)}
              placeholder="Min Price"
              className="bg-black border border-gray-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:border-orange-500 transition-colors placeholder-gray-500"
            />
            <input
              type="number"
              value={maxPrice}
              onChange={(e) => setMaxPrice(e.target.value)}
              placeholder="Max Price"
              className="bg-black border border-gray-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:border-orange-500 transition-colors placeholder-gray-500"
            />
          </div>
        </div>
      </div>

      {/* Results Section */}
      <div className="max-w-7xl mx-auto px-4 py-12">
        {error && (
          <div className="bg-red-900/20 border border-red-500 text-red-400 px-6 py-4 rounded-lg mb-8">
            <p className="font-semibold">Unable to load coaches</p>
            <p className="text-sm mt-1">{error.message || "Backend service is currently offline."}</p>
            <button 
              onClick={() => refetch()} 
              className="mt-3 text-orange-500 hover:text-orange-400 underline text-sm"
            >
              Try Again
            </button>
          </div>
        )}

        {isLoading && (
          <div className="flex justify-center py-20">
            <div className="text-orange-500 text-lg">Loading luxury coaches...</div>
          </div>
        )}

        {data && data.length === 0 && (
          <div className="text-center py-20">
            <p className="text-gray-400 text-lg">No coaches found matching your criteria.</p>
            <p className="text-gray-500 mt-2">Try adjusting your search filters.</p>
          </div>
        )}

        {data && data.length > 0 && (
          <>
            <div className="flex justify-between items-center mb-6">
              <p className="text-gray-400">
                Found <span className="text-orange-500 font-semibold">{data.length}</span> luxury coaches
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {data.map((c) => <CoachCard key={c.id} c={c} />)}
            </div>
          </>
        )}

        {/* Placeholder content when no data */}
        {!data && !isLoading && !error && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="rounded-lg overflow-hidden shadow-lg bg-gray-900 border border-gray-800">
                <div className="aspect-video bg-gray-800 animate-pulse"></div>
                <div className="p-4">
                  <div className="h-6 bg-gray-800 rounded animate-pulse mb-2"></div>
                  <div className="h-8 bg-gray-800 rounded animate-pulse w-3/4 mb-2"></div>
                  <div className="h-4 bg-gray-800 rounded animate-pulse w-1/2"></div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-800 mt-20">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <p className="text-center text-gray-500">
            © 2025 PrevostGo - Premium Luxury Coach Marketplace
          </p>
        </div>
      </footer>
    </div>
  );
}
