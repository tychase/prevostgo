export const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export async function api<T>(path: string, params: Record<string, any> = {}): Promise<T> {
  const u = new URL(API_URL + path);
  Object.entries(params).forEach(([k,v]) => {
    if (v !== undefined && v !== null && v !== "") u.searchParams.set(k, String(v));
  });
  const r = await fetch(u.toString());
  if (!r.ok) throw new Error(`API ${r.status}`);
  return r.json();
}
