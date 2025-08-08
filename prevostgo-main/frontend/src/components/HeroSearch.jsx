import React, { useState, useMemo } from 'react';
import { Search, ChevronDown } from 'lucide-react';
import PriceSlider from './PriceSlider';
import CustomSelect from './CustomSelect';

/**
 * Hero Search Component
 * The main search interface on the homepage.
 */
const HeroSearch = ({ onSearch }) => {
  const [isAdvancedOpen, setIsAdvancedOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [priceRange, setPriceRange] = useState([50000, 3000000]);
  const [converter, setConverter] = useState('');
  const [chassis, setChassis] = useState('');
  const [slides, setSlides] = useState('');
  const [yearRange, setYearRange] = useState([2015, new Date().getFullYear()]);
  
  const handleSearch = () => {
      onSearch({
          searchTerm,
          priceRange,
          converter,
          chassis,
          slides,
          yearRange
      });
  };

  const converters = useMemo(() => ["Marathon", "Liberty", "Newell", "Foretravel", "Millennium", "Emerald"], []);
  const chassisTypes = useMemo(() => ["H3-45", "XLII", "XL", "X3"], []);
  const slideOptions = useMemo(() => ["1", "2", "3", "4", "5"], []);

  return (
    <div className="relative z-10 w-full max-w-4xl mx-auto">
      <div className="bg-black/30 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl shadow-black/50 p-4 md:p-6 overflow-visible">
        <div className="relative flex items-center">
          <Search className="absolute left-4 w-6 h-6 text-gray-500" />
          <input
            type="text"
            placeholder="Search by model, year, or keyword..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full py-4 pl-14 pr-48 bg-gray-900/50 text-white placeholder-gray-400 border border-transparent rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500/80 transition-shadow duration-300 shadow-inner"
          />
          <button 
            onClick={handleSearch}
            className="absolute right-2 top-1/2 -translate-y-1/2 px-6 py-3 bg-amber-600 text-white font-bold rounded-lg hover:bg-amber-500 transform hover:scale-105 transition-all duration-300 shadow-lg shadow-amber-600/20"
          >
            Search
          </button>
        </div>
        
        <div className="mt-4 text-center">
            <button
                onClick={() => setIsAdvancedOpen(!isAdvancedOpen)}
                className="inline-flex items-center px-4 py-2 text-sm text-gray-300 hover:text-white transition-colors"
            >
                Advanced Filters
                <ChevronDown className={`w-5 h-5 ml-2 transition-transform duration-300 ${isAdvancedOpen ? 'rotate-180' : ''}`} />
            </button>
        </div>

        <div className={`transition-all duration-500 ease-in-out ${isAdvancedOpen ? 'max-h-[1000px] opacity-100 overflow-visible' : 'max-h-0 opacity-0 overflow-hidden'}`}>
            <div className="pt-6 border-t border-white/10">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6 relative">
                    <div className="md:col-span-2">
                        <label className="block mb-2 text-sm font-medium text-gray-400">Price Range</label>
                        <PriceSlider
                            min={50000}
                            max={3000000}
                            step={50000}
                            values={priceRange}
                            onChange={setPriceRange}
                        />
                    </div>
                    <div className="relative">
                        <CustomSelect label="Converter / Manufacturer" options={converters} value={converter} onChange={setConverter} placeholder="Any Converter" />
                    </div>
                    <div className="relative">
                        <CustomSelect label="Chassis Type" options={chassisTypes} value={chassis} onChange={setChassis} placeholder="Any Chassis" />
                    </div>
                    <div className="relative">
                        <CustomSelect label="Number of Slides" options={slideOptions} value={slides} onChange={setSlides} placeholder="Any" />
                    </div>
                    <div>
                      <label className="block mb-2 text-sm font-medium text-gray-400">Year Range</label>
                      <div className="flex items-center space-x-4">
                        <input type="number" value={yearRange[0]} onChange={e => setYearRange([e.target.value, yearRange[1]])} className="w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500/50" />
                        <span className="text-gray-500">-</span>
                        <input type="number" value={yearRange[1]} onChange={e => setYearRange([yearRange[0], e.target.value])} className="w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500/50" />
                      </div>
                    </div>
                </div>
            </div>
        </div>
      </div>
    </div>
  );
};

export default HeroSearch;
