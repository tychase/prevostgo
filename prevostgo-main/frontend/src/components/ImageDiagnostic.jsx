import React, { useEffect, useState } from 'react';
import { searchCoaches } from '../services/api';

const ImageDiagnostic = () => {
    const [coaches, setCoaches] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchCoaches = async () => {
            try {
                const response = await searchCoaches({ per_page: 10 });
                console.log('Raw API Response:', response);
                console.log('Coaches data:', response.data?.coaches);
                setCoaches(response.data?.coaches || []);
            } catch (err) {
                console.error('Error fetching coaches:', err);
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };
        fetchCoaches();
    }, []);

    if (loading) return <div className="p-8">Loading...</div>;
    if (error) return <div className="p-8 text-red-500">Error: {error}</div>;

    return (
        <div className="p-8">
            <h2 className="text-2xl font-bold mb-4">Image Diagnostic</h2>
            <div className="space-y-4">
                {coaches.map((coach, index) => (
                    <div key={coach.id || index} className="border p-4 rounded">
                        <h3 className="font-semibold">{coach.title}</h3>
                        <div className="mt-2">
                            <p className="text-sm text-gray-600">Images array: {JSON.stringify(coach.images)}</p>
                            <p className="text-sm text-gray-600">First image: {coach.images?.[0] || 'No image'}</p>
                            {coach.images && coach.images.length > 0 && (
                                <div className="mt-2">
                                    <p className="text-sm">Testing image load:</p>
                                    <img 
                                        src={coach.images[0]} 
                                        alt="Test" 
                                        className="mt-1 h-32 w-48 object-cover border"
                                        onLoad={(e) => console.log('Image loaded:', coach.images[0])}
                                        onError={(e) => {
                                            console.error('Image failed to load:', coach.images[0]);
                                            console.error('Error event:', e);
                                        }}
                                    />
                                </div>
                            )}
                        </div>
                    </div>
                ))}
            </div>
            <div className="mt-8">
                <h3 className="font-semibold">Summary:</h3>
                <p>Total coaches: {coaches.length}</p>
                <p>Coaches with images: {coaches.filter(c => c.images && c.images.length > 0).length}</p>
                <p>Coaches without images: {coaches.filter(c => !c.images || c.images.length === 0).length}</p>
            </div>
        </div>
    );
};

export default ImageDiagnostic;
