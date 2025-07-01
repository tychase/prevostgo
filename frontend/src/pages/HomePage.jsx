import React, { useState, useEffect } from 'react';
import { ArrowRight } from 'lucide-react';
import HeroSearch from '../components/HeroSearch';
import CoachGrid from '../components/CoachGrid';
import api from '../services/api';

/**
 * Home Page Component
 * The main landing page with hero search and featured listings.
 */
const HomePage = () => {
    const [coaches, setCoaches] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchApplied, setSearchApplied] = useState(false);
    const [totalCoaches, setTotalCoaches] = useState(0);

    // Fetch initial coaches
    useEffect(() => {
        fetchCoaches();
    }, []);

    const fetchCoaches = async (filters = {}) => {
        setLoading(true);
        setError(null);
        try {
            const response = await api.searchCoaches({
            per_page: 6,
            sort_by: 'price',
                sort_order: 'desc',
            ...filters
        });
            setCoaches(response.data.coaches || []);
            setTotalCoaches(response.data.total || 0);
        } catch (error) {
            console.error('Error fetching coaches:', error);
            setError('Unable to load coaches. Please ensure the backend server is running.');
            setCoaches([]);
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = async (filters) => {
        console.log("Searching with filters:", filters);
        setSearchApplied(true);
        
        // Convert the filters to API format
        const apiFilters = {
            search: filters.searchTerm,
            price_min: filters.priceRange[0],
            price_max: filters.priceRange[1],
            converter: filters.converter || undefined,
            chassis: filters.chassis || undefined,
            slide_count: filters.slides ? parseInt(filters.slides) : undefined,
            year_min: filters.yearRange[0],
            year_max: filters.yearRange[1]
        };

        // Remove undefined values
        Object.keys(apiFilters).forEach(key => 
            apiFilters[key] === undefined && delete apiFilters[key]
        );

        await fetchCoaches(apiFilters);
    };

    return (
        <div className="w-full">
            {/* Hero Section */}
            <div className="relative flex items-center justify-center min-h-[70vh] md:min-h-[80vh] w-full overflow-hidden p-4">
                <div className="absolute inset-0 bg-gradient-to-b from-black/30 via-black/80 to-[#0a0a0a] z-0"></div>
                <div className="absolute inset-0 bg-cover bg-center bg-[url('https://placehold.co/1920x1080/0a0a0a/d4af37?text=PrevostGO')] opacity-20 blur-sm scale-110"></div>
                <div className="relative z-10 flex flex-col items-center text-center text-white">
                    <p className="mt-4 max-w-3xl text-2xl md:text-3xl lg:text-4xl font-light text-gray-100 drop-shadow-lg leading-relaxed">
                        Discover an exclusive collection of the world's finest Prevost conversions. Your journey begins here.
                    </p>
                    <div className="w-full mt-12">
                        <HeroSearch onSearch={handleSearch} />
                    </div>
                </div>
            </div>

            {/* Featured Listings Section */}
            <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
                <div className="flex justify-between items-center mb-12">
                     <h2 className="text-3xl md:text-4xl font-bold text-white tracking-tight">
                        {searchApplied ? `Search Results (${totalCoaches} found)` : 'Featured Inventory'}
                     </h2>
                     <a href="/inventory" className="group inline-flex items-center text-amber-400 hover:text-amber-300 transition-colors">
                        View All Inventory
                        <ArrowRight className="w-4 h-4 ml-2 transition-transform duration-300 group-hover:translate-x-1" />
                     </a>
                </div>
                {error && (
                    <div className="mb-8 p-4 bg-red-900/20 border border-red-600/50 rounded-lg text-red-200">
                        <p className="text-sm font-semibold">{error}</p>
                        <p className="text-xs mt-2">Start the backend server with: <code className="bg-black/50 px-2 py-1 rounded">python main.py</code></p>
                    </div>
                )}
                <CoachGrid coaches={coaches} loading={loading} />
                {searchApplied && totalCoaches > 6 && (
                    <div className="text-center mt-8">
                        <p className="text-gray-400 mb-4">Showing 6 of {totalCoaches} results</p>
                        <a href="/inventory" className="inline-flex items-center px-6 py-3 bg-amber-600 text-white font-semibold rounded-lg hover:bg-amber-500 transition-colors">
                            View All Results
                            <ArrowRight className="w-4 h-4 ml-2" />
                        </a>
                    </div>
                )}
            </main>
        </div>
    );
};

export default HomePage;
