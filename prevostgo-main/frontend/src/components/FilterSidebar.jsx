import { Fragment } from 'react';
import { Disclosure } from '@headlessui/react';
import { ChevronUpIcon } from '@heroicons/react/24/outline';

const priceRanges = [
  { label: 'Under $200k', min: null, max: 200000 },
  { label: '$200k - $500k', min: 200000, max: 500000 },
  { label: '$500k - $1M', min: 500000, max: 1000000 },
  { label: 'Over $1M', min: 1000000, max: null },
];

export default function FilterSidebar({ filters, facets, onChange }) {
  const handleCheckboxChange = (filterKey, value) => {
    const currentValues = filters[filterKey] || [];
    const newValues = currentValues.includes(value)
      ? currentValues.filter(v => v !== value)
      : [...currentValues, value];
    
    onChange({ ...filters, [filterKey]: newValues });
  };

  const handleRangeChange = (filterKey, value) => {
    onChange({ ...filters, [filterKey]: value ? parseInt(value) : null });
  };

  const handlePriceRangeSelect = (range) => {
    onChange({
      ...filters,
      price_min: range.min,
      price_max: range.max,
    });
  };

  const clearFilters = () => {
    onChange({
      ...filters,
      price_min: null,
      price_max: null,
      year_min: null,
      year_max: null,
      mileage_max: null,
      models: [],
      converters: [],
      slide_counts: [],
      conditions: [],
      dealer_states: [],
    });
  };

  const hasActiveFilters = 
    filters.price_min || filters.price_max ||
    filters.year_min || filters.year_max ||
    filters.mileage_max ||
    filters.models?.length > 0 ||
    filters.converters?.length > 0 ||
    filters.slide_counts?.length > 0 ||
    filters.conditions?.length > 0 ||
    filters.dealer_states?.length > 0;

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900">Filters</h2>
        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="text-sm text-primary-600 hover:text-primary-700"
          >
            Clear all
          </button>
        )}
      </div>

      <div className="space-y-6">
        {/* Price Range */}
        <Disclosure defaultOpen>
          {({ open }) => (
            <>
              <Disclosure.Button className="flex w-full justify-between rounded-lg bg-gray-50 px-4 py-2 text-left text-sm font-medium text-gray-900 hover:bg-gray-100 focus:outline-none focus-visible:ring focus-visible:ring-primary-500 focus-visible:ring-opacity-75">
                <span>Price Range</span>
                <ChevronUpIcon
                  className={`${open ? 'rotate-180 transform' : ''} h-5 w-5 text-gray-500`}
                />
              </Disclosure.Button>
              <Disclosure.Panel className="px-4 pt-4 pb-2">
                <div className="space-y-2">
                  {priceRanges.map((range) => (
                    <button
                      key={range.label}
                      onClick={() => handlePriceRangeSelect(range)}
                      className={`w-full text-left px-3 py-2 rounded text-sm ${
                        filters.price_min === range.min && filters.price_max === range.max
                          ? 'bg-primary-100 text-primary-700'
                          : 'hover:bg-gray-100'
                      }`}
                    >
                      {range.label}
                    </button>
                  ))}
                </div>
                <div className="mt-4 space-y-3">
                  <div>
                    <label className="label text-xs">Min Price</label>
                    <input
                      type="number"
                      value={filters.price_min || ''}
                      onChange={(e) => handleRangeChange('price_min', e.target.value)}
                      className="input-field text-sm"
                      placeholder="0"
                    />
                  </div>
                  <div>
                    <label className="label text-xs">Max Price</label>
                    <input
                      type="number"
                      value={filters.price_max || ''}
                      onChange={(e) => handleRangeChange('price_max', e.target.value)}
                      className="input-field text-sm"
                      placeholder="Any"
                    />
                  </div>
                </div>
              </Disclosure.Panel>
            </>
          )}
        </Disclosure>

        {/* Year */}
        <Disclosure defaultOpen>
          {({ open }) => (
            <>
              <Disclosure.Button className="flex w-full justify-between rounded-lg bg-gray-50 px-4 py-2 text-left text-sm font-medium text-gray-900 hover:bg-gray-100 focus:outline-none focus-visible:ring focus-visible:ring-primary-500 focus-visible:ring-opacity-75">
                <span>Year</span>
                <ChevronUpIcon
                  className={`${open ? 'rotate-180 transform' : ''} h-5 w-5 text-gray-500`}
                />
              </Disclosure.Button>
              <Disclosure.Panel className="px-4 pt-4 pb-2">
                <div className="space-y-3">
                  <div>
                    <label className="label text-xs">Min Year</label>
                    <input
                      type="number"
                      value={filters.year_min || ''}
                      onChange={(e) => handleRangeChange('year_min', e.target.value)}
                      className="input-field text-sm"
                      placeholder="1990"
                    />
                  </div>
                  <div>
                    <label className="label text-xs">Max Year</label>
                    <input
                      type="number"
                      value={filters.year_max || ''}
                      onChange={(e) => handleRangeChange('year_max', e.target.value)}
                      className="input-field text-sm"
                      placeholder={new Date().getFullYear().toString()}
                    />
                  </div>
                </div>
              </Disclosure.Panel>
            </>
          )}
        </Disclosure>

        {/* Model */}
        {facets?.models && Object.keys(facets.models).length > 0 && (
          <Disclosure defaultOpen>
            {({ open }) => (
              <>
                <Disclosure.Button className="flex w-full justify-between rounded-lg bg-gray-50 px-4 py-2 text-left text-sm font-medium text-gray-900 hover:bg-gray-100 focus:outline-none focus-visible:ring focus-visible:ring-primary-500 focus-visible:ring-opacity-75">
                  <span>Model</span>
                  <ChevronUpIcon
                    className={`${open ? 'rotate-180 transform' : ''} h-5 w-5 text-gray-500`}
                  />
                </Disclosure.Button>
                <Disclosure.Panel className="px-4 pt-4 pb-2">
                  <div className="space-y-2">
                    {Object.entries(facets.models).map(([model, count]) => (
                      <label key={model} className="flex items-center">
                        <input
                          type="checkbox"
                          checked={filters.models?.includes(model) || false}
                          onChange={() => handleCheckboxChange('models', model)}
                          className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                        />
                        <span className="ml-2 text-sm text-gray-700">
                          {model} ({count})
                        </span>
                      </label>
                    ))}
                  </div>
                </Disclosure.Panel>
              </>
            )}
          </Disclosure>
        )}

        {/* Converter */}
        {facets?.converters && Object.keys(facets.converters).length > 0 && (
          <Disclosure>
            {({ open }) => (
              <>
                <Disclosure.Button className="flex w-full justify-between rounded-lg bg-gray-50 px-4 py-2 text-left text-sm font-medium text-gray-900 hover:bg-gray-100 focus:outline-none focus-visible:ring focus-visible:ring-primary-500 focus-visible:ring-opacity-75">
                  <span>Converter</span>
                  <ChevronUpIcon
                    className={`${open ? 'rotate-180 transform' : ''} h-5 w-5 text-gray-500`}
                  />
                </Disclosure.Button>
                <Disclosure.Panel className="px-4 pt-4 pb-2">
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    {Object.entries(facets.converters)
                      .sort(([, a], [, b]) => b - a)
                      .map(([converter, count]) => (
                        <label key={converter} className="flex items-center">
                          <input
                            type="checkbox"
                            checked={filters.converters?.includes(converter) || false}
                            onChange={() => handleCheckboxChange('converters', converter)}
                            className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                          />
                          <span className="ml-2 text-sm text-gray-700">
                            {converter} ({count})
                          </span>
                        </label>
                      ))}
                  </div>
                </Disclosure.Panel>
              </>
            )}
          </Disclosure>
        )}

        {/* Slides */}
        {facets?.slide_counts && Object.keys(facets.slide_counts).length > 0 && (
          <Disclosure>
            {({ open }) => (
              <>
                <Disclosure.Button className="flex w-full justify-between rounded-lg bg-gray-50 px-4 py-2 text-left text-sm font-medium text-gray-900 hover:bg-gray-100 focus:outline-none focus-visible:ring focus-visible:ring-primary-500 focus-visible:ring-opacity-75">
                  <span>Slides</span>
                  <ChevronUpIcon
                    className={`${open ? 'rotate-180 transform' : ''} h-5 w-5 text-gray-500`}
                  />
                </Disclosure.Button>
                <Disclosure.Panel className="px-4 pt-4 pb-2">
                  <div className="space-y-2">
                    {Object.entries(facets.slide_counts)
                      .sort(([a], [b]) => parseInt(a) - parseInt(b))
                      .map(([slides, count]) => (
                        <label key={slides} className="flex items-center">
                          <input
                            type="checkbox"
                            checked={filters.slide_counts?.includes(parseInt(slides)) || false}
                            onChange={() => handleCheckboxChange('slide_counts', parseInt(slides))}
                            className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                          />
                          <span className="ml-2 text-sm text-gray-700">
                            {slides} Slides ({count})
                          </span>
                        </label>
                      ))}
                  </div>
                </Disclosure.Panel>
              </>
            )}
          </Disclosure>
        )}

        {/* Condition */}
        <Disclosure>
          {({ open }) => (
            <>
              <Disclosure.Button className="flex w-full justify-between rounded-lg bg-gray-50 px-4 py-2 text-left text-sm font-medium text-gray-900 hover:bg-gray-100 focus:outline-none focus-visible:ring focus-visible:ring-primary-500 focus-visible:ring-opacity-75">
                <span>Condition</span>
                <ChevronUpIcon
                  className={`${open ? 'rotate-180 transform' : ''} h-5 w-5 text-gray-500`}
                />
              </Disclosure.Button>
              <Disclosure.Panel className="px-4 pt-4 pb-2">
                <div className="space-y-2">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={filters.conditions?.includes('new') || false}
                      onChange={() => handleCheckboxChange('conditions', 'new')}
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">New</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={filters.conditions?.includes('pre-owned') || false}
                      onChange={() => handleCheckboxChange('conditions', 'pre-owned')}
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">Pre-Owned</span>
                  </label>
                </div>
              </Disclosure.Panel>
            </>
          )}
        </Disclosure>

        {/* Mileage */}
        <Disclosure>
          {({ open }) => (
            <>
              <Disclosure.Button className="flex w-full justify-between rounded-lg bg-gray-50 px-4 py-2 text-left text-sm font-medium text-gray-900 hover:bg-gray-100 focus:outline-none focus-visible:ring focus-visible:ring-primary-500 focus-visible:ring-opacity-75">
                <span>Mileage</span>
                <ChevronUpIcon
                  className={`${open ? 'rotate-180 transform' : ''} h-5 w-5 text-gray-500`}
                />
              </Disclosure.Button>
              <Disclosure.Panel className="px-4 pt-4 pb-2">
                <div>
                  <label className="label text-xs">Max Mileage</label>
                  <input
                    type="number"
                    value={filters.mileage_max || ''}
                    onChange={(e) => handleRangeChange('mileage_max', e.target.value)}
                    className="input-field text-sm"
                    placeholder="Any"
                  />
                </div>
              </Disclosure.Panel>
            </>
          )}
        </Disclosure>
      </div>
    </div>
  );
}
