import { useState } from 'react';
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline';

export default function ImageGallery({ images = [], alt = 'Coach image' }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  
  // Use placeholder if no images
  const displayImages = images.length > 0 ? images : ['/placeholder-coach.jpg'];

  const handlePrevious = () => {
    setCurrentIndex((prev) => (prev - 1 + displayImages.length) % displayImages.length);
  };

  const handleNext = () => {
    setCurrentIndex((prev) => (prev + 1) % displayImages.length);
  };

  return (
    <div className="relative">
      {/* Main Image */}
      <div className="aspect-w-16 aspect-h-12 bg-gray-200 rounded-lg overflow-hidden">
        <img
          src={displayImages[currentIndex]}
          alt={`${alt} ${currentIndex + 1}`}
          className="w-full h-full object-cover"
          onError={(e) => {
            e.target.src = '/placeholder-coach.jpg';
          }}
        />
      </div>

      {/* Navigation Arrows */}
      {displayImages.length > 1 && (
        <>
          <button
            onClick={handlePrevious}
            className="absolute left-4 top-1/2 -translate-y-1/2 bg-black/50 text-white p-2 rounded-full hover:bg-black/70 transition-colors"
          >
            <ChevronLeftIcon className="h-6 w-6" />
          </button>
          <button
            onClick={handleNext}
            className="absolute right-4 top-1/2 -translate-y-1/2 bg-black/50 text-white p-2 rounded-full hover:bg-black/70 transition-colors"
          >
            <ChevronRightIcon className="h-6 w-6" />
          </button>
        </>
      )}

      {/* Thumbnails */}
      {displayImages.length > 1 && (
        <div className="mt-4 grid grid-cols-6 gap-2">
          {displayImages.slice(0, 6).map((image, index) => (
            <button
              key={index}
              onClick={() => setCurrentIndex(index)}
              className={`aspect-w-16 aspect-h-12 rounded overflow-hidden ${
                currentIndex === index ? 'ring-2 ring-primary-600' : ''
              }`}
            >
              <img
                src={image}
                alt={`Thumbnail ${index + 1}`}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.target.src = '/placeholder-coach.jpg';
                }}
              />
            </button>
          ))}
        </div>
      )}

      {/* Image Counter */}
      {displayImages.length > 1 && (
        <div className="absolute bottom-4 right-4 bg-black/50 text-white px-3 py-1 rounded-full text-sm">
          {currentIndex + 1} / {displayImages.length}
        </div>
      )}
    </div>
  );
}
