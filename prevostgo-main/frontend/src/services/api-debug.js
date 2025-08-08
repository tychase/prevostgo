// Debug file to check environment variables at build time
console.log('=== API DEBUG INFO ===');
console.log('Build Time:', new Date().toISOString());
console.log('VITE_API_URL from env:', import.meta.env.VITE_API_URL);
console.log('NODE_ENV:', import.meta.env.NODE_ENV);
console.log('MODE:', import.meta.env.MODE);
console.log('All VITE vars:', Object.keys(import.meta.env).filter(k => k.startsWith('VITE_')));

export const debugInfo = {
  buildTime: new Date().toISOString(),
  apiUrl: import.meta.env.VITE_API_URL,
  mode: import.meta.env.MODE,
  env: import.meta.env.NODE_ENV
};
