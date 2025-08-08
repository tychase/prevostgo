// Use relative URL in production (Vercel handles the proxy)
// Use full URL in development
const isProduction = import.meta.env.PROD;
export const API_URL = isProduction ? "/api" : (import.meta.env.VITE_API_URL || "http://localhost:8000/api");

export async function api(path, params = {}) {
  const u = new URL(API_URL + path, window.location.origin);
  Object.entries(params).forEach(([k,v]) => {
    if (v !== undefined && v !== null && v !== "") u.searchParams.set(k, String(v));
  });
  const r = await fetch(u.toString());
  if (!r.ok) throw new Error(`API ${r.status}`);
  return r.json();
}
