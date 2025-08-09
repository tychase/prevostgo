import { useState } from "react";
import { api } from "../api/client";
import { useQuery } from "@tanstack/react-query";

function CoachCard({ c }) {
  return (
    <div className="rounded-lg overflow-hidden shadow-lg bg-gray-900 border border-gray-800 hover:border-orange-500 transition-all duration-300 group cursor-pointer">
      <div className="aspect-video bg-gray-800 relative overflow-hidden">
        {c.photos?.[0] && (
          <img 
            src={c.photos[0]} 
            alt={c.title} 
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" 
            loading="lazy" 
          />
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
        <div className="absolute top-4 right-4 bg-black/70 backdrop-blur-sm px-3 py-1 rounded-full">
          <span className="text-orange-500 font-semibold text-sm">{c.year || "NEW"}</span>
        </div>
      </div>
      <div className="p-4">
        <div className="font-bold text-white text-lg line-clamp-1">{c.title || `${c.year || ""} ${c.model || ""}`}</div>
        <div className="text-orange-500 font-semibold text-xl mt-1">
          ${c.price?.toLocaleString?.() || "Contact for Price"}
        </div>
        <div className="text-gray-400 text-sm mt-2 flex items-center gap-2">
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
          </svg>
          {c.location || "Location TBD"}
        </div>
      </div>
    </div>
  );
}

export default function SearchPage() {
  const [activeTab, setActiveTab] = useState("buy");
  const [q, setQ] = useState("");
  const [sort, setSort] = useState("newest");
  const [minYear, setMinYear] = useState("");
  const [maxYear, setMaxYear] = useState("");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [showFilters, setShowFilters] = useState(false);

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

  const handleSearch = () => {
    refetch();
  };

  return (
    <div className="min-h-screen bg-black">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <h1 className="text-3xl font-bold text-white">PrevostGo</h1>
              <span className="text-orange-500 text-sm font-semibold uppercase tracking-wider">Luxury Coaches</span>
            </div>
            <nav className="flex items-center gap-6">
              <a href="#" className="text-gray-400 hover:text-white transition-colors">About</a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">Contact</a>
              <button className="bg-orange-500 text-black px-6 py-2 rounded-full font-semibold hover:bg-orange-400 transition-colors">
                List Your Coach
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Search Section */}
      <div className="bg-gradient-to-b from-gray-900 via-gray-900/95 to-black py-16">
        <div className="max-w-5xl mx-auto px-4">
          <h2 className="text-4xl md:text-5xl font-bold text-white text-center mb-8">
            Find Your Perfect Luxury Coach
          </h2>
          
          {/* Search Bar with Tabs */}
          <div className="bg-gray-900 rounded-2xl shadow-2xl border border-gray-800 overflow-hidden">
            {/* Buy/Sell Tabs */}
            <div className="flex">
              <button
                onClick={() => setActiveTab("buy")}
                className={`flex-1 py-4 px-6 font-semibold text-lg transition-all ${
                  activeTab === "buy"
                    ? "bg-orange-500 text-black"
                    : "bg-gray-800 text-gray-400 hover:text-white hover:bg-gray-700"
                }`}
              >
                Buy a Coach
              </button>
              <button
                onClick={() => setActiveTab("sell")}
                className={`flex-1 py-4 px-6 font-semibold text-lg transition-all ${
                  activeTab === "sell"
                    ? "bg-orange-500 text-black"
                    : "bg-gray-800 text-gray-400 hover:text-white hover:bg-gray-700"
                }`}
              >
                Sell Your Coach
              </button>
            </div>

            {/* Search Content */}
            <div className="p-6">
              {activeTab === "buy" ? (
                <>
                  <div className="flex flex-col lg:flex-row gap-4">
                    <div className="flex-1 relative">
                      <input
                        value={q}
                        onChange={(e) => setQ(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                        placeholder="Search by make, model, year, or converter..."
                        className="w-full bg-black border-2 border-gray-700 text-white rounded-xl px-6 py-4 pr-12 focus:outline-none focus:border-orange-500 transition-colors placeholder-gray-500 text-lg"
                      />
                      <svg 
                        className="absolute right-4 top-1/2 -translate-y-1/2 w-6 h-6 text-gray-500"
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                    </div>
                    <select 
                      value={sort} 
                      onChange={(e) => setSort(e.target.value)} 
                      className="bg-black border-2 border-gray-700 text-white rounded-xl px-6 py-4 focus:outline-none focus:border-orange-500 transition-colors min-w-[180px]"
                    >
                      <option value="newest">Newest First</option>
                      <option value="oldest">Oldest First</option>
                      <option value="price_high">Price: High to Low</option>
                      <option value="price_low">Price: Low to High</option>
                    </select>
                    <button 
                      onClick={handleSearch} 
                      className="px-8 py-4 rounded-xl bg-orange-500 text-black font-bold hover:bg-orange-400 transition-all duration-300 shadow-lg hover:shadow-orange-500/25 text-lg"
                      disabled={isLoading}
                    >
                      {isLoading ? "Searching..." : "Search"}
                    </button>
                  </div>

                  {/* Toggle Advanced Filters */}
                  <button
                    onClick={() => setShowFilters(!showFilters)}
                    className="mt-4 text-orange-500 hover:text-orange-400 font-semibold flex items-center gap-2"
                  >
                    <svg 
                      className="w-5 h-5" 
                      fill="none" 
                      stroke="currentColor" 
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                    </svg>
                    {showFilters ? "Hide" : "Show"} Advanced Filters
                  </button>

                  {/* Advanced Filters */}
                  {showFilters && (
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-6 p-6 bg-black/50 rounded-xl">
                      <div>
                        <label className="text-gray-400 text-sm mb-2 block">Min Year</label>
                        <input
                          type="number"
                          value={minYear}
                          onChange={(e) => setMinYear(e.target.value)}
                          placeholder="e.g. 2015"
                          className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:border-orange-500 transition-colors placeholder-gray-600"
                        />
                      </div>
                      <div>
                        <label className="text-gray-400 text-sm mb-2 block">Max Year</label>
                        <input
                          type="number"
                          value={maxYear}
                          onChange={(e) => setMaxYear(e.target.value)}
                          placeholder="e.g. 2024"
                          className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:border-orange-500 transition-colors placeholder-gray-600"
                        />
                      </div>
                      <div>
                        <label className="text-gray-400 text-sm mb-2 block">Min Price ($)</label>
                        <input
                          type="number"
                          value={minPrice}
                          onChange={(e) => setMinPrice(e.target.value)}
                          placeholder="e.g. 500000"
                          className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:border-orange-500 transition-colors placeholder-gray-600"
                        />
                      </div>
                      <div>
                        <label className="text-gray-400 text-sm mb-2 block">Max Price ($)</label>
                        <input
                          type="number"
                          value={maxPrice}
                          onChange={(e) => setMaxPrice(e.target.value)}
                          placeholder="e.g. 2000000"
                          className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:border-orange-500 transition-colors placeholder-gray-600"
                        />
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <div className="text-center py-8">
                  <h3 className="text-2xl font-bold text-white mb-4">Sell Your Luxury Coach</h3>
                  <p className="text-gray-400 mb-6">Get maximum exposure to qualified buyers</p>
                  <button className="bg-orange-500 text-black px-8 py-4 rounded-xl font-bold hover:bg-orange-400 transition-all duration-300 shadow-lg hover:shadow-orange-500/25 text-lg">
                    Start Listing Process
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-3 gap-4 mt-8">
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-500">500+</div>
              <div className="text-gray-400 text-sm">Luxury Coaches</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-500">$2M+</div>
              <div className="text-gray-400 text-sm">Average Price</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-500">48hrs</div>
              <div className="text-gray-400 text-sm">Average Sale Time</div>
            </div>
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
              <div className="flex gap-2">
                <button className="p-2 rounded-lg bg-gray-900 border border-gray-800 text-gray-400 hover:text-white hover:border-gray-700">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                  </svg>
                </button>
                <button className="p-2 rounded-lg bg-gray-900 border border-gray-800 text-gray-400 hover:text-white hover:border-gray-700">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                  </svg>
                </button>
              </div>
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
      <footer className="border-t border-gray-800 mt-20 bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-white font-bold text-lg mb-4">PrevostGo</h3>
              <p className="text-gray-400 text-sm">The premier marketplace for luxury Prevost coaches.</p>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Buy</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-gray-400 hover:text-orange-500 text-sm">Browse Coaches</a></li>
                <li><a href="#" className="text-gray-400 hover:text-orange-500 text-sm">Advanced Search</a></li>
                <li><a href="#" className="text-gray-400 hover:text-orange-500 text-sm">Financing</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Sell</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-gray-400 hover:text-orange-500 text-sm">List Your Coach</a></li>
                <li><a href="#" className="text-gray-400 hover:text-orange-500 text-sm">Pricing Guide</a></li>
                <li><a href="#" className="text-gray-400 hover:text-orange-500 text-sm">Seller Resources</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Connect</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-gray-400 hover:text-orange-500 text-sm">Contact Us</a></li>
                <li><a href="#" className="text-gray-400 hover:text-orange-500 text-sm">About</a></li>
                <li><a href="#" className="text-gray-400 hover:text-orange-500 text-sm">Support</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center">
            <p className="text-gray-500 text-sm">
              © 2025 PrevostGo. All rights reserved. | Premium Luxury Coach Marketplace
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
