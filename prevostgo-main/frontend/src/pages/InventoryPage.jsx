import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import HeroSearch from '../components/HeroSearch';
import CoachGrid from '../components/CoachGrid';
import SortDropdown from '../components/SortDropdown';
import api from '../services/api';

const InventoryPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [coaches, setCoaches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [totalCoaches, setTotalCoaches] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [sortBy, setSortBy] = useState('price_desc');
  const coachesPerPage = 12;

  useEffect(() => {
    fetchCoaches();
  }, [searchParams, currentPage, sortBy]); // Add currentPage and sortBy as dependencies

  const fetchCoaches = async () => {
    setLoading(true);
    try {
      // Parse sort settings
      const [sortField, sortOrder] = sortBy.split('_');
      
      const params = {
        per_page: coachesPerPage,
        page: currentPage,
        search: searchParams.get('search') || undefined,
        price_min: searchParams.get('price_min') || undefined,
        price_max: searchParams.get('price_max') || undefined,
        converter: searchParams.get('converter') || undefined,
        chassis: searchParams.get('chassis') || undefined,
        slide_count: searchParams.get('slides') ? parseInt(searchParams.get('slides')) : undefined,
        year_min: searchParams.get('year_min') || undefined,
        year_max: searchParams.get('year_max') || undefined,
        sort_by: sortField === 'created' ? 'created_at' : sortField,
        sort_order: sortOrder || 'desc',
      };

      // Remove undefined values
      Object.keys(params).forEach(key => 
        params[key] === undefined && delete params[key]
      );

      const response = await api.searchCoaches(params);
      setCoaches(response.data.coaches || []);
      setTotalCoaches(response.data.total || 0);
    } catch (error) {
      console.error('Error fetching coaches:', error);
      setCoaches([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (filters) => {
    const newParams = new URLSearchParams();
    
    if (filters.searchTerm) newParams.set('search', filters.searchTerm);
    if (filters.priceRange[0] > 50000) newParams.set('price_min', filters.priceRange[0]);
    if (filters.priceRange[1] < 3000000) newParams.set('price_max', filters.priceRange[1]);
    if (filters.converter) newParams.set('converter', filters.converter);
    if (filters.chassis) newParams.set('chassis', filters.chassis);
    if (filters.slides) newParams.set('slides', filters.slides);
    if (filters.yearRange[0] > 2015) newParams.set('year_min', filters.yearRange[0]);
    if (filters.yearRange[1] < new Date().getFullYear()) newParams.set('year_max', filters.yearRange[1]);
    
    setSearchParams(newParams);
    setCurrentPage(1);
  };

  const handleSortChange = (newSort) => {
    setSortBy(newSort);
    setCurrentPage(1);
  };

  const totalPages = Math.ceil(totalCoaches / coachesPerPage);

  return (
    <div className="w-full pt-20">
      {/* Search Section */}
      <div className="bg-gradient-to-b from-black via-gray-900 to-[#0a0a0a] py-12">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl md:text-4xl font-bold text-white text-center mb-8">
            Browse Our Inventory
          </h1>
          <HeroSearch onSearch={handleSearch} />
        </div>
      </div>

      {/* Results Section */}
      <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
          <h2 className="text-2xl font-bold text-white">
            {totalCoaches} Coaches Found
          </h2>
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
            <SortDropdown value={sortBy} onChange={handleSortChange} />
            {totalPages > 1 && (
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className="px-4 py-2 bg-gray-800 text-white rounded-lg disabled:opacity-50"
              >
                Previous
              </button>
              <span className="text-gray-400">
                Page {currentPage} of {totalPages}
              </span>
              <button
                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
                className="px-4 py-2 bg-gray-800 text-white rounded-lg disabled:opacity-50"
              >
                Next
              </button>
            </div>
            )}
          </div>
        </div>
        <CoachGrid coaches={coaches} loading={loading} />
      </main>
    </div>
  );
};

export default InventoryPage;
