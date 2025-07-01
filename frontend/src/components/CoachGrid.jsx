import React from 'react';
import CoachCard from './CoachCard';

/**
 * Coach Grid Component
 * Displays a grid of CoachCard components.
 */
const CoachGrid = ({ coaches, loading }) => {
    if (loading) {
        return (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {[...Array(6)].map((_, i) => (
                    <div key={i} className="rounded-2xl bg-gray-900/50 p-4 animate-pulse">
                        <div className="h-64 bg-gray-800 rounded-lg"></div>
                        <div className="mt-4 space-y-3">
                            <div className="h-4 bg-gray-800 rounded w-3/4"></div>
                            <div className="h-4 bg-gray-800 rounded w-1/2"></div>
                        </div>
                    </div>
                ))}
            </div>
        );
    }
    
    if (!coaches || coaches.length === 0) {
        return (
            <div className="text-center py-20">
                <h2 className="text-2xl font-bold text-white">No Coaches Found</h2>
                <p className="text-gray-400 mt-2">Try adjusting your search filters.</p>
            </div>
        )
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
            {coaches.map(coach => <CoachCard key={coach.id} coach={coach} />)}
        </div>
    );
};

export default CoachGrid;
