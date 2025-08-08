import { useState, useEffect } from 'react';

export default function DebugPage() {
  const [results, setResults] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const runTests = async () => {
      const debugInfo = {
        timestamp: new Date().toISOString(),
        env: {
          VITE_API_URL: import.meta.env.VITE_API_URL,
          MODE: import.meta.env.MODE,
          PROD: import.meta.env.PROD,
          DEV: import.meta.env.DEV,
          BASE_URL: import.meta.env.BASE_URL,
        },
        location: {
          href: window.location.href,
          protocol: window.location.protocol,
          host: window.location.host,
        }
      };

      // Test direct fetch to backend
      try {
        const testUrl = 'https://prevostgo-production.up.railway.app/api/health';
        const response = await fetch(testUrl);
        const data = await response.json();
        debugInfo.directFetch = {
          success: true,
          url: testUrl,
          data: data
        };
      } catch (error) {
        debugInfo.directFetch = {
          success: false,
          error: error.message
        };
      }

      setResults(debugInfo);
      setLoading(false);
    };

    runTests();
  }, []);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-4">Debug Information</h1>
      
      {loading ? (
        <p>Loading debug information...</p>
      ) : (
        <div className="bg-gray-100 p-4 rounded">
          <pre className="whitespace-pre-wrap">
            {JSON.stringify(results, null, 2)}
          </pre>
        </div>
      )}

      <div className="mt-8">
        <h2 className="text-xl font-bold mb-2">Quick Actions</h2>
        <button 
          onClick={() => window.location.reload(true)}
          className="bg-blue-500 text-white px-4 py-2 rounded mr-2"
        >
          Hard Reload
        </button>
        <button 
          onClick={() => {
            localStorage.clear();
            sessionStorage.clear();
            alert('Cache cleared! Reloading...');
            window.location.reload(true);
          }}
          className="bg-red-500 text-white px-4 py-2 rounded"
        >
          Clear Cache & Reload
        </button>
      </div>
    </div>
  );
}