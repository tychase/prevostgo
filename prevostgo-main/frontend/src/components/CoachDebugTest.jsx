import { useState, useEffect } from 'react';
import { inventoryAPI } from '../services/api';

export default function CoachDebugTest() {
  const [coaches, setCoaches] = useState([]);
  const [selectedCoach, setSelectedCoach] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch list of coaches
    inventoryAPI.getCoaches({ per_page: 5 })
      .then(response => {
        console.log('Coaches list response:', response.data);
        setCoaches(response.data.coaches || []);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching coaches:', err);
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const fetchCoachDetail = async (coach) => {
    console.log('Fetching detail for coach:', coach);
    console.log('Coach ID:', coach.id);
    console.log('Coach ID type:', typeof coach.id);
    
    try {
      const response = await inventoryAPI.getCoach(coach.id);
      console.log('Detail response:', response);
      setSelectedCoach(response.data);
    } catch (err) {
      console.error('Error fetching coach detail:', err);
      if (err.response) {
        console.error('Response error:', err.response.data);
        console.error('Response status:', err.response.status);
      }
      setError(`Failed to fetch coach: ${err.message}`);
    }
  };

  if (loading) return <div className="p-8">Loading...</div>;
  if (error) return <div className="p-8 text-red-600">Error: {error}</div>;

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Coach Debug Test</h1>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <h2 className="text-xl font-semibold mb-2">Coaches List</h2>
          {coaches.length === 0 ? (
            <p>No coaches found</p>
          ) : (
            <ul className="space-y-2">
              {coaches.map(coach => (
                <li key={coach.id} className="border p-2 rounded">
                  <div>ID: {coach.id}</div>
                  <div>Title: {coach.title}</div>
                  <button
                    onClick={() => fetchCoachDetail(coach)}
                    className="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                  >
                    Fetch Details
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
        
        <div>
          <h2 className="text-xl font-semibold mb-2">Selected Coach Details</h2>
          {selectedCoach ? (
            <div className="border p-4 rounded">
              <pre className="text-xs overflow-x-auto">
                {JSON.stringify(selectedCoach, null, 2)}
              </pre>
            </div>
          ) : (
            <p className="text-gray-500">Click a coach to see details</p>
          )}
        </div>
      </div>
    </div>
  );
}
