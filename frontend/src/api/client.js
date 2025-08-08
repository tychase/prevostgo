// API configuration
const isProduction = import.meta.env.PROD;
const isDevelopment = import.meta.env.DEV;

// In production, use the Vercel proxy. In development, use local or Railway
export const API_URL = isProduction 
  ? "/api" 
  : (import.meta.env.VITE_API_URL || "http://localhost:8000/api");

export async function api(path, params = {}) {
  try {
    // Build the URL
    const baseUrl = isProduction ? window.location.origin + API_URL : API_URL;
    const u = new URL(baseUrl + path);
    
    // Add query parameters
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") {
        u.searchParams.set(k, String(v));
      }
    });
    
    console.log(`Fetching: ${u.toString()}`);
    
    // Make the request
    const response = await fetch(u.toString(), {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      mode: isProduction ? 'same-origin' : 'cors',
    });
    
    // Check if response is ok
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`API Error ${response.status}:`, errorText);
      throw new Error(`API Error ${response.status}: ${response.statusText}`);
    }
    
    // Parse JSON
    const data = await response.json();
    return data;
    
  } catch (error) {
    console.error('API Request failed:', error);
    throw error;
  }
}
