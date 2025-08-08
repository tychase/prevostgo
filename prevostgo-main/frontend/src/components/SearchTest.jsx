import React, { useState } from 'react';
import api from '../services/api';

const SearchTest = () => {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('Marathon');

  const testSearch = async () => {
    setLoading(true);
    try {
      console.log('Testing search with term:', searchTerm);
      
      // Test 1: Direct API call with search
      const response = await api.searchCoaches({
        search: searchTerm,
        per_page: 5
      });
      
      console.log('Full response:', response);
      setResults(response.data);
    } catch (error) {
      console.error('Search test error:', error);
      setResults({ error: error.message });
    }
    setLoading(false);
  };

  const testFilters = async () => {
    setLoading(true);
    try {
      console.log('Testing filters');
      
      // Test 2: Price filter
      const response = await api.searchCoaches({
        min_price: 100000,
        max_price: 1000000,
        per_page: 5
      });
      
      console.log('Filter response:', response);
      setResults(response.data);
    } catch (error) {
      console.error('Filter test error:', error);
      setResults({ error: error.message });
    }
    setLoading(false);
  };

  return (
    <div className="p-8 bg-gray-900 text-white min-h-screen">
      <h1 className="text-2xl font-bold mb-4">Search API Test</h1>
      
      <div className="mb-4">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="px-4 py-2 bg-gray-800 text-white rounded mr-2"
          placeholder="Search term"
        />
        <button
          onClick={testSearch}
          className="px-4 py-2 bg-blue-600 text-white rounded mr-2"
          disabled={loading}
        >
          Test Search
        </button>
        <button
          onClick={testFilters}
          className="px-4 py-2 bg-green-600 text-white rounded"
          disabled={loading}
        >
          Test Filters
        </button>
      </div>

      {loading && <p>Loading...</p>}
      
      {results && (
        <pre className="bg-gray-800 p-4 rounded overflow-auto">
          {JSON.stringify(results, null, 2)}
        </pre>
      )}
    </div>
  );
};

export default SearchTest;