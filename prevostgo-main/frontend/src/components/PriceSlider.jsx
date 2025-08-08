import React, { useState, useEffect, useRef } from 'react';

/**
 * Custom Price Range Slider Component
 * A dual-thumb slider for selecting a price range.
 */
const PriceSlider = ({ min, max, step, values, onChange }) => {
  const [minVal, setMinVal] = useState(values[0]);
  const [maxVal, setMaxVal] = useState(values[1]);
  const range = useRef(null);

  useEffect(() => {
    setMinVal(values[0]);
    setMaxVal(values[1]);
  }, [values]);

  const formatCurrency = (value) => {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    }
    if (value >= 1000) {
      return `$${Math.round(value / 1000)}k`;
    }
    return `$${value}`;
  };

  const getPercent = (value) => Math.round(((value - min) / (max - min)) * 100);

  const handleMinChange = (e) => {
    const value = Math.min(Number(e.target.value), maxVal - step);
    setMinVal(value);
    onChange([value, maxVal]);
  };

  const handleMaxChange = (e) => {
    const value = Math.max(Number(e.target.value), minVal + step);
    setMaxVal(value);
    onChange([minVal, value]);
  };

  const minPercent = getPercent(minVal);
  const maxPercent = getPercent(maxVal);

  return (
    <div className="relative w-full py-4">
      <div className="relative h-1 bg-gray-700 rounded-full">
        <div
          ref={range}
          className="absolute h-1 bg-amber-500 rounded-full"
          style={{ left: `${minPercent}%`, width: `${maxPercent - minPercent}%` }}
        ></div>
        <div className="absolute flex justify-between w-full -top-3 px-0.5">
            <span className="text-xs text-gray-400">{formatCurrency(min)}</span>
            <span className="text-xs text-gray-400 pr-2">{formatCurrency(max)}</span>
        </div>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={minVal}
        onChange={handleMinChange}
        className="absolute w-[calc(100%-16px)] h-1 bg-transparent appearance-none pointer-events-auto top-4 left-2"
        style={{ zIndex: 3 }}
      />
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={maxVal}
        onChange={handleMaxChange}
        className="absolute w-[calc(100%-16px)] h-1 bg-transparent appearance-none pointer-events-auto top-4 left-2"
        style={{ zIndex: 4 }}
      />
      <div className="flex justify-between mt-4">
        <div className="px-3 py-1 text-sm text-white bg-gray-800 border border-gray-700 rounded-md">
          {formatCurrency(minVal)}
        </div>
        <div className="px-3 py-1 text-sm text-white bg-gray-800 border border-gray-700 rounded-md">
          {formatCurrency(maxVal)}
        </div>
      </div>
    </div>
  );
};

export default PriceSlider;
