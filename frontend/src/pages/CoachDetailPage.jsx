import { useParams, Link, useLocation, useNavigate } from 'react-router-dom';
import { useQuery } from 'react-query';
import { useState, useEffect, useRef } from 'react';
import { 
  ArrowLeftIcon, 
  HeartIcon, 
  ShareIcon, 
  VideoCameraIcon,
  CheckCircleIcon,
  PhoneIcon,
  EnvelopeIcon,
  MapPinIcon,
  CalendarIcon,
  TruckIcon,
  CogIcon,
  SparklesIcon,
  HomeIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';
import { HeartIcon as HeartIconSolid } from '@heroicons/react/24/solid';
import { inventoryAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ImageGallery from '../components/ImageGallery';
import InquiryForm from '../components/InquiryForm';
import SimilarCoaches from '../components/SimilarCoaches';
import toast from 'react-hot-toast';

export default function CoachDetailPage() {
  const { coachId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [showInquiryForm, setShowInquiryForm] = useState(false);
  const [isFavorite, setIsFavorite] = useState(false);
  const previousLocationRef = useRef(null);

  // Track where we came from
  useEffect(() => {
    // Store the referrer if we have one
    if (location.state?.from) {
      previousLocationRef.current = location.state.from;
    }
  }, [location]);

  const { data: response, isLoading, error } = useQuery(
    ['coach', coachId],
    () => inventoryAPI.getCoach(coachId),
    {
      onError: (error) => {
        console.error('Error fetching coach:', error);
        if (error.response) {
          console.error('Response data:', error.response.data);
          console.error('Response status:', error.response.status);
        }
      },
    }
  );

  // Extract coach data from response
  const coach = response?.data || response;

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: coach?.title || 'Prevost Coach',
        text: `Check out this ${coach?.year} ${coach?.converter} ${coach?.model}`,
        url: window.location.href,
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      toast.success('Link copied to clipboard!');
    }
  };

  const toggleFavorite = () => {
    setIsFavorite(!isFavorite);
    toast.success(isFavorite ? 'Removed from favorites' : 'Added to favorites');
  };

  const handleBackClick = () => {
    // Check if we have a previous location stored with query parameters
    const backPath = location.state?.from || previousLocationRef.current;
    
    if (backPath) {
      // Navigate back to the exact path including search params
      navigate(backPath);
    } else {
      // Default to inventory page if no previous location
      navigate('/inventory');
    }
  };

  if (isLoading) return <LoadingSpinner size="large" className="py-20" />;
  if (error) {
    return (
      <div className="text-center py-20">
        <p className="text-red-600 text-lg font-semibold">Error loading coach details</p>
        <p className="text-gray-600 mt-2">
          {error.response?.status === 404 
            ? 'Coach not found' 
            : error.response?.data?.detail || error.message || 'An unexpected error occurred'}
        </p>
        <button
          onClick={handleBackClick}
          className="inline-flex items-center mt-4 text-primary-600 hover:text-primary-700"
        >
          <ArrowLeftIcon className="h-5 w-5 mr-2" />
          Back to Inventory
        </button>
      </div>
    );
  }
  if (!coach) return <div className="text-center py-20">Coach not found</div>;

  // Log coach data for debugging
  console.log('Coach data:', coach);

  const formatPrice = (price) => {
    if (!price) return 'Contact for Price';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  const getSpecIcon = (spec) => {
    const icons = {
      year: CalendarIcon,
      model: TruckIcon,
      converter: SparklesIcon,
      engine: CogIcon,
      chassis: TruckIcon,
      bathroom: HomeIcon,
      mileage: ChartBarIcon
    };
    return icons[spec] || CheckCircleIcon;
  };

  return (
    <div className="bg-gray-50 min-h-screen">
      {/* Back button */}
      <div className="bg-white shadow-sm sticky top-0 z-10">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-4">
          <button
            onClick={handleBackClick}
            className="inline-flex items-center text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeftIcon className="h-5 w-5 mr-2" />
            Back to Inventory
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Image Gallery */}
          <div className="lg:sticky lg:top-24 lg:self-start">
            <ImageGallery images={coach.images || []} alt={coach.title} />
            
            {/* Virtual Tour Button */}
            {coach.virtual_tour_url && (
              <div className="mt-4">
                <a
                  href={coach.virtual_tour_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2 w-full px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-xl hover:from-primary-700 hover:to-primary-800 transition-all duration-300 shadow-lg"
                >
                  <VideoCameraIcon className="h-5 w-5" />
                  Take Virtual Tour
                </a>
              </div>
            )}
          </div>

          {/* Details */}
          <div>
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-3xl lg:text-4xl font-display font-bold text-gray-900 mb-4">
                {coach.title || `${coach.year} ${coach.converter || ''} ${coach.model || ''}`.trim()}
              </h1>
              
              <div className="flex items-center justify-between mb-6">
                <div>
                  <p className="text-4xl font-bold text-primary-600">
                    {formatPrice(coach.price) || coach.price_display || 'Contact for Price'}
                  </p>
                  {coach.price && (
                    <p className="text-sm text-gray-500 mt-1">Plus taxes & fees</p>
                  )}
                </div>
                <div className="flex gap-2">
                  <button 
                    onClick={toggleFavorite}
                    className="p-3 rounded-full border border-gray-300 hover:bg-gray-50 transition-colors"
                  >
                    {isFavorite ? (
                      <HeartIconSolid className="h-6 w-6 text-red-500" />
                    ) : (
                      <HeartIcon className="h-6 w-6 text-gray-600" />
                    )}
                  </button>
                  <button
                    onClick={handleShare}
                    className="p-3 rounded-full border border-gray-300 hover:bg-gray-50 transition-colors"
                  >
                    <ShareIcon className="h-6 w-6 text-gray-600" />
                  </button>
                </div>
              </div>

              {/* Condition Badge */}
              <div className="flex items-center gap-4">
                <span className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium ${
                  coach.condition === 'new' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-blue-100 text-blue-800'
                }`}>
                  {coach.condition === 'new' ? 'Brand New' : 'Pre-Owned'}
                </span>
                {coach.stock_number && (
                  <span className="text-sm text-gray-500">
                    Stock #: {coach.stock_number}
                  </span>
                )}
              </div>
            </div>

            {/* Key Details Grid */}
            <div className="grid grid-cols-2 gap-4 mb-8">
              <div className="bg-white p-5 rounded-xl border border-gray-200 hover:shadow-md transition-shadow">
                <div className="flex items-center gap-3">
                  <ChartBarIcon className="h-8 w-8 text-primary-600" />
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Mileage</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {coach.mileage ? coach.mileage.toLocaleString() + ' miles' : 'Not specified'}
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white p-5 rounded-xl border border-gray-200 hover:shadow-md transition-shadow">
                <div className="flex items-center gap-3">
                  <HomeIcon className="h-8 w-8 text-primary-600" />
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Slides</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {coach.slide_count || 0} {coach.slide_count === 1 ? 'Slide' : 'Slides'}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Features Section */}
            {coach.features && coach.features.length > 0 && (
              <div className="mb-8">
                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  <SparklesIcon className="h-6 w-6 text-primary-600" />
                  Premium Features
                </h2>
                <div className="flex flex-wrap gap-2">
                  {coach.features.map((feature, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center gap-1 bg-gradient-to-r from-primary-50 to-primary-100 text-primary-700 px-4 py-2 rounded-full text-sm font-medium"
                    >
                      <CheckCircleIcon className="h-4 w-4" />
                      {feature}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Specifications Grid */}
            <div className="mb-8">
              <h2 className="text-xl font-semibold mb-4">Detailed Specifications</h2>
              <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                <div className="divide-y divide-gray-200">
                  {coach.year && (
                    <div className="flex items-center justify-between p-4 hover:bg-gray-50 transition-colors">
                      <div className="flex items-center gap-3">
                        <CalendarIcon className="h-5 w-5 text-gray-400" />
                        <span className="text-gray-600">Year</span>
                      </div>
                      <span className="font-medium text-gray-900">{coach.year}</span>
                    </div>
                  )}
                  {coach.model && (
                    <div className="flex items-center justify-between p-4 hover:bg-gray-50 transition-colors">
                      <div className="flex items-center gap-3">
                        <TruckIcon className="h-5 w-5 text-gray-400" />
                        <span className="text-gray-600">Model</span>
                      </div>
                      <span className="font-medium text-gray-900">{coach.model}</span>
                    </div>
                  )}
                  {coach.converter && (
                    <div className="flex items-center justify-between p-4 hover:bg-gray-50 transition-colors">
                      <div className="flex items-center gap-3">
                        <SparklesIcon className="h-5 w-5 text-gray-400" />
                        <span className="text-gray-600">Converter</span>
                      </div>
                      <span className="font-medium text-gray-900">{coach.converter}</span>
                    </div>
                  )}
                  {coach.engine && (
                    <div className="flex items-center justify-between p-4 hover:bg-gray-50 transition-colors">
                      <div className="flex items-center gap-3">
                        <CogIcon className="h-5 w-5 text-gray-400" />
                        <span className="text-gray-600">Engine</span>
                      </div>
                      <span className="font-medium text-gray-900">{coach.engine}</span>
                    </div>
                  )}
                  {coach.chassis_type && (
                    <div className="flex items-center justify-between p-4 hover:bg-gray-50 transition-colors">
                      <div className="flex items-center gap-3">
                        <TruckIcon className="h-5 w-5 text-gray-400" />
                        <span className="text-gray-600">Chassis Type</span>
                      </div>
                      <span className="font-medium text-gray-900">{coach.chassis_type}</span>
                    </div>
                  )}
                  {coach.bathroom_config && (
                    <div className="flex items-center justify-between p-4 hover:bg-gray-50 transition-colors">
                      <div className="flex items-center gap-3">
                        <HomeIcon className="h-5 w-5 text-gray-400" />
                        <span className="text-gray-600">Bathroom Configuration</span>
                      </div>
                      <span className="font-medium text-gray-900">{coach.bathroom_config}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Dealer Information Card */}
            <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-6 text-white mb-8">
              <h2 className="text-xl font-semibold mb-4">Dealer Information</h2>
              <div className="space-y-3">
                <div className="font-medium text-lg">
                  {coach.dealer_name || 'Authorized Prevost Dealer'}
                </div>
                {coach.dealer_state && (
                  <div className="flex items-center gap-2 text-gray-300">
                    <MapPinIcon className="h-5 w-5" />
                    <span>{coach.dealer_state}</span>
                  </div>
                )}
                {coach.dealer_phone && (
                  <div>
                    <a
                      href={`tel:${coach.dealer_phone}`}
                      className="flex items-center gap-2 text-gray-300 hover:text-white transition-colors"
                    >
                      <PhoneIcon className="h-5 w-5" />
                      <span>{coach.dealer_phone}</span>
                    </a>
                  </div>
                )}
                {coach.dealer_email && (
                  <div>
                    <a
                      href={`mailto:${coach.dealer_email}`}
                      className="flex items-center gap-2 text-gray-300 hover:text-white transition-colors"
                    >
                      <EnvelopeIcon className="h-5 w-5" />
                      <span>{coach.dealer_email}</span>
                    </a>
                  </div>
                )}
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="space-y-3">
              <button
                onClick={() => setShowInquiryForm(true)}
                className="w-full px-8 py-4 bg-gradient-to-r from-primary-600 to-primary-700 text-white font-semibold rounded-xl hover:from-primary-700 hover:to-primary-800 transform hover:scale-[1.02] transition-all duration-300 shadow-lg"
              >
                Request More Information
              </button>
              <button className="w-full px-8 py-4 bg-white text-gray-900 font-semibold rounded-xl border-2 border-gray-300 hover:border-gray-400 hover:bg-gray-50 transform hover:scale-[1.02] transition-all duration-300">
                Schedule a Viewing
              </button>
              {coach.dealer_phone && (
                <a
                  href={`tel:${coach.dealer_phone}`}
                  className="w-full px-8 py-4 bg-green-600 text-white font-semibold rounded-xl hover:bg-green-700 transform hover:scale-[1.02] transition-all duration-300 shadow-lg flex items-center justify-center gap-2"
                >
                  <PhoneIcon className="h-5 w-5" />
                  Call Dealer Now
                </a>
              )}
            </div>
          </div>
        </div>

        {/* Similar Coaches Section */}
        <div className="mt-20 pt-12 border-t border-gray-200">
          <h2 className="text-3xl font-display font-bold mb-8">You May Also Like</h2>
          <SimilarCoaches currentCoachId={coachId} converter={coach?.converter} model={coach?.model} />
        </div>
      </div>

      {/* Inquiry Modal */}
      {showInquiryForm && (
        <InquiryForm
          coach={coach}
          onClose={() => setShowInquiryForm(false)}
          onSuccess={() => {
            setShowInquiryForm(false);
            toast.success('Your inquiry has been sent!');
          }}
        />
      )}
    </div>
  );
}
