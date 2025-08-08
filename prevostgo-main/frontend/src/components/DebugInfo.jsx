import { useEffect, useState } from 'react';

export default function DebugInfo() {
  const [info, setInfo] = useState({});

  useEffect(() => {
    const debugInfo = {
      VITE_API_URL: import.meta.env.VITE_API_URL,
      NODE_ENV: import.meta.env.NODE_ENV,
      MODE: import.meta.env.MODE,
      BASE_URL: import.meta.env.BASE_URL,
      PROD: import.meta.env.PROD,
      DEV: import.meta.env.DEV,
      SSR: import.meta.env.SSR,
      // Check what axios will use
      windowLocation: window.location.href,
      protocol: window.location.protocol,
    };

    setInfo(debugInfo);

    // Log to console too
    console.log('=== DEBUG INFO ===');
    Object.entries(debugInfo).forEach(([key, value]) => {
      console.log(`${key}:`, value);
    });
    console.log('=================');
  }, []);

  if (import.meta.env.PROD) {
    return null; // Don't show in production unless there's an issue
  }

  return (
    <div style={{
      position: 'fixed',
      bottom: 0,
      right: 0,
      background: 'black',
      color: 'white',
      padding: '10px',
      fontSize: '12px',
      maxWidth: '300px',
      zIndex: 9999
    }}>
      <h4>Debug Info</h4>
      <pre>{JSON.stringify(info, null, 2)}</pre>
    </div>
  );
}