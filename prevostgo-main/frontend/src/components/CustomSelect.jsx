import React, { useState, useEffect, useRef } from 'react';
import { ChevronDown } from 'lucide-react';

/**
 * Custom Select Dropdown Component
 * A styled dropdown that matches the luxury theme.
 */
const CustomSelect = ({ label, options, value, onChange, placeholder }) => {
    const [isOpen, setIsOpen] = useState(false);
    const selectRef = useRef(null);

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (selectRef.current && !selectRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const handleSelect = (optionValue) => {
        onChange(optionValue);
        setIsOpen(false);
    };

    return (
        <div className="relative w-full" ref={selectRef}>
            <label className="block mb-2 text-sm font-medium text-gray-400">{label}</label>
            <button
                type="button"
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center justify-between w-full px-4 py-3 text-left bg-gray-800/50 border border-gray-700 rounded-lg shadow-sm backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-amber-500/50"
            >
                <span className="text-white">{value || placeholder}</span>
                <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform duration-300 ${isOpen ? 'transform rotate-180' : ''}`} />
            </button>
            {isOpen && (
                <div className="absolute z-50 w-full mt-1 bg-gray-900 border border-gray-700 rounded-lg shadow-xl max-h-60 overflow-y-auto">
                    <ul className="py-1">
                        <li
                            onClick={() => handleSelect('')}
                            className="px-4 py-2 text-gray-400 cursor-pointer hover:bg-amber-600/20 hover:text-white transition-colors"
                        >
                            {placeholder}
                        </li>
                        {options.map((option, index) => (
                            <li
                                key={index}
                                onClick={() => handleSelect(option)}
                                className="px-4 py-2 text-white cursor-pointer hover:bg-amber-600/20 transition-colors"
                            >
                                {option}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};

export default CustomSelect;
