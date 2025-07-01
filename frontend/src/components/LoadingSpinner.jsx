export default function LoadingSpinner({ size = 'default', className = '' }) {
  const sizeClasses = {
    small: 'w-6 h-6',
    default: 'w-10 h-10',
    large: 'w-16 h-16',
  };

  return (
    <div className={`flex justify-center items-center ${className}`}>
      <div className={`loading-spinner ${sizeClasses[size]}`}></div>
    </div>
  );
}
