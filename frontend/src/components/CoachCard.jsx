import React from 'react';
import { Link, useLocation } from 'react-router-dom';

/**
 * Coach Card Component
 * Displays a single coach listing in a card format.
 */
const CoachCard = ({ coach }) => {
    const location = useLocation();
    
    const formatCurrency = (value) => {
        if (value >= 1000000) {
            return `$${(value / 1000000).toFixed(1)}M`;
        }
        if (value >= 1000) {
            return `$${Math.round(value / 1000)}k`;
        }
        return `$${value}`;
    };

    return (
        <div className="group relative overflow-hidden rounded-2xl bg-black/30 backdrop-blur-lg border border-white/10 transition-all duration-500 hover:border-amber-500/50 hover:shadow-2xl hover:shadow-amber-900/50">
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent z-10"></div>
            <img 
                src={coach.images?.[0] || 'https://placehold.co/600x400/0a0a0a/333333?text=No+Image'} 
                alt={coach.title} 
                className="w-full h-64 object-cover transition-transform duration-500 group-hover:scale-110" 
                onError={(e) => { e.target.onerror = null; e.target.src = 'https://placehold.co/600x400/0a0a0a/333333?text=Image+Not+Found'; }}
            />
            <div className="absolute bottom-0 left-0 right-0 p-6 z-20 text-white">
                <h3 className="text-xl font-bold leading-tight truncate">{coach.title}</h3>
                <div className="flex justify-between items-end mt-2">
                    <div>
                        <p className="text-lg font-semibold text-amber-400">
                            {coach.price ? formatCurrency(coach.price) : coach.price_display || 'Contact for Price'}
                        </p>
                        <p className="text-sm text-gray-400">{`${coach.year} • ${coach.converter}`}</p>
                    </div>
                    <div className="flex items-center space-x-2 text-sm text-gray-300">
                        <span>{`${coach.slide_count || 0} Slides`}</span>
                    </div>
                </div>
            </div>
             <Link 
                to={`/inventory/${coach.id}`} 
                state={{ from: location.pathname + location.search }}
                className="absolute inset-0 z-30" 
                aria-label={`View details for ${coach.title}`}
            ></Link>
        </div>
    );
};

export default CoachCard;
