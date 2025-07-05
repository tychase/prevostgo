import axios from 'axios';

// Use environment variable for production, proxy for development
let apiUrl = import.meta.env.VITE_API_URL || '/api';

// Debug logging
console.log('Original VITE_API_URL:', import.meta.env.VITE_API_URL);
console.log('Initial apiUrl:', apiUrl);

// Ensure HTTPS in production - force HTTPS for any production URL
if (apiUrl.includes('railway.app') || apiUrl.includes('prevostgo')) {
  // Always use HTTPS for production URLs
  if (!apiUrl.startsWith('https://')) {
    if (apiUrl.startsWith('http://')) {
      console.warn('Production URL using HTTP, forcing HTTPS');
      apiUrl = apiUrl.replace('http://', 'https://');
    } else if (!apiUrl.startsWith('/')) {
      // If no protocol, add https://
      console.warn('No protocol specified, adding HTTPS');
      apiUrl = 'https://' + apiUrl;
    }
  }
}

const API_URL = apiUrl;
console.log('Final API_URL:', API_URL);

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth (when implemented)
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Force HTTPS for production requests
    if (config.url && (config.url.includes('railway.app') || config.url.includes('prevostgo'))) {
      if (config.url.startsWith('http://')) {
        console.warn('Interceptor: Forcing HTTPS for request:', config.url);
        config.url = config.url.replace('http://', 'https://');
      }
    }
    
    // Also check baseURL
    if (config.baseURL && (config.baseURL.includes('railway.app') || config.baseURL.includes('prevostgo'))) {
      if (config.baseURL.startsWith('http://')) {
        console.warn('Interceptor: Forcing HTTPS for baseURL:', config.baseURL);
        config.baseURL = config.baseURL.replace('http://', 'https://');
      }
    }
    
    console.log('Final request config:', config.method, config.baseURL + config.url);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Main search function
export const searchCoaches = async (params = {}) => {
  try {
    // Clean up params - remove empty strings and undefined values
    const cleanParams = Object.entries(params).reduce((acc, [key, value]) => {
      if (value !== undefined && value !== '' && value !== null) {
        acc[key] = value;
      }
      return acc;
    }, {});
    
    console.log('Searching with params:', cleanParams);
    console.log('API URL:', api.defaults.baseURL + '/inventory');
    
    const response = await api.get('/inventory', { params: cleanParams });
    console.log('API Response:', response.data);
    return response;
  } catch (error) {
    console.error('Search error:', error);
    if (error.response) {
      console.error('Error response:', error.response.data);
      console.error('Error status:', error.response.status);
    } else if (error.request) {
      console.error('No response received:', error.request);
    } else {
      console.error('Error setting up request:', error.message);
    }
    throw error;
  }
};

// Inventory endpoints
export const inventoryAPI = {
  getCoaches: (params) => api.get('/inventory', { params }),
  getCoach: (id) => {
    console.log('Fetching coach with ID:', id);
    const url = `/inventory/${id}`;
    console.log('Request URL:', url);
    return api.get(url);
  },
  getFeatured: (limit = 6) => api.get('/featured', { params: { limit } }),
  getSummary: () => api.get('/inventory/summary'),
  updateCoach: (id, data) => api.put(`/inventory/${id}`, data),
  trackEvent: (event) => api.post('/inventory/track-event', event),
};

// Search endpoints
export const searchAPI = {
  searchCoaches: (filters) => api.post('/search/coaches', filters),
  getSuggestions: (q, field = 'all') => api.get('/search/suggestions', { params: { q, field } }),
  getFacets: () => api.get('/search/facets'),
  findSimilar: (coachId, limit = 6) => api.post(`/search/similar/${coachId}`, { limit }),
};

// Lead endpoints
export const leadAPI = {
  createLead: (data) => api.post('/leads/', data),
  createInquiry: (data) => api.post('/leads/inquiry', data),
  trackView: (leadId, coachId) => api.post(`/leads/${leadId}/track-view`, { coach_id: coachId }),
};

// Search alert endpoints
export const alertAPI = {
  createAlert: (leadId, data) => api.post('/search/alerts', { ...data, lead_id: leadId }),
  getAlert: (id) => api.get(`/search/alerts/${id}`),
  toggleAlert: (id) => api.put(`/search/alerts/${id}/toggle`),
  deleteAlert: (id) => api.delete(`/search/alerts/${id}`),
  getLeadAlerts: (leadId, activeOnly = true) => 
    api.get(`/search/alerts/lead/${leadId}`, { params: { active_only: activeOnly } }),
};

export default { ...api, searchCoaches };
