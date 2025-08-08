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
  const [sort, setSort] = useState("relevance");
  const [minYear, setMinYear] = useState("");
  const [maxYear, setMaxYear] = useState("");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["search", q, sort, minYear, maxYear, minPrice, maxPrice],
    queryFn: () => api("/coaches/search", {
      q,
      sort,
      min_year: minYear || undefined,
      max_year: maxYear || undefined,
      min_price: minPrice || undefined,
      max_price: maxPrice || undefined,
      page: 1, page_size: 24
    }),
  });

  return (
    <div className="max-w-7xl mx-auto p-4 flex flex-col gap-4">
      <div className="flex flex-col md:flex-row gap-3">
        <input
          value={q}
          onChange={(e)=>setQ(e.target.value)}
          placeholder="Search by year, model, converter..."
          className="flex-1 border rounded-xl px-4 py-3"
        />
        <select value={sort} onChange={(e)=>setSort(e.target.value)} className="border rounded-xl px-3 py-3">
          <option value="relevance">Relevance</option>
          <option value="year_desc">Newest</option>
          <option value="price_desc">Price: High → Low</option>
          <option value="price_asc">Price: Low → High</option>
        </select>
        <button onClick={()=>refetch()} className="px-4 py-3 rounded-xl bg-black text-white">Search</button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {isLoading && <div>Loading...</div>}
        {error && <div className="text-red-600">Error loading coaches</div>}
        {data?.map((c) => <CoachCard key={c.id} c={c} />)}
      </div>
    </div>
  );
}
