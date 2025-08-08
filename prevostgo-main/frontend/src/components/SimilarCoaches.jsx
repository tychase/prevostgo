import { useQuery } from 'react-query';
import { Link, useLocation } from 'react-router-dom';
import { inventoryAPI } from '../services/api';
import LoadingSpinner from './LoadingSpinner';

export default function SimilarCoaches({ currentCoachId, converter, model }) {
  const location = useLocation();
  const { data: similarCoaches, isLoading } = useQuery(
    ['similar-coaches', currentCoachId],
    async () => {
      // Get coaches with similar converter or model
      const response = await inventoryAPI.getCoaches({
        per_page: 4,
        converter: converter,
        sort_by: 'price',
        sort_order: 'asc'
      });
      
      // Filter out the current coach and limit to 3
      const coaches = response.data.coaches
        .filter(coach => coach.id !== currentCoachId)
        .slice(0, 3);
      
      return coaches;
    },
    {
      enabled: !!converter || !!model,
    }
  );

  if (isLoading) {
    return <LoadingSpinner size="small" />;
  }

  if (!similarCoaches || similarCoaches.length === 0) {
    return (
      <p className="text-gray-600">No similar coaches available at this time.</p>
    );
  }

  const formatPrice = (price) => {
    if (!price) return 'Contact for Price';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {similarCoaches.map((coach) => (
        <Link
          key={coach.id}
          to={`/inventory/${coach.id}`}
          state={{ from: location.pathname + location.search }}
          className="group"
        >
          <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
            <div className="aspect-w-16 aspect-h-9 bg-gray-200">
              {coach.images && coach.images.length > 0 ? (
                <img
                  src={coach.images[0]}
                  alt={coach.title}
                  className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.src = 'https://placehold.co/600x400/1a1a1a/666666?text=No+Image';
                  }}
                />
              ) : (
                <div className="w-full h-48 bg-gray-300 flex items-center justify-center">
                  <span className="text-gray-500">No Image</span>
                </div>
              )}
            </div>
            <div className="p-4">
              <h3 className="font-semibold text-lg mb-2 line-clamp-2">
                {coach.title || `${coach.year} ${coach.converter} ${coach.model}`}
              </h3>
              <p className="text-xl font-bold text-primary-600">
                {formatPrice(coach.price)}
              </p>
              <div className="flex justify-between mt-2 text-sm text-gray-600">
                <span>{coach.year}</span>
                <span>{coach.mileage ? `${coach.mileage.toLocaleString()} miles` : 'Mileage N/A'}</span>
              </div>
            </div>
          </div>
        </Link>
      ))}
    </div>
  );
}
