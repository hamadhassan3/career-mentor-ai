const Logo = ({ size = 'md', className = '', rounded = true, title }) => {
  const sizeClasses = {
    header: 'w-12 h-12',
    sm: 'w-8 h-8',
    md: 'w-20 h-20',
    lg: 'w-24 h-24',
    xl: 'w-32 h-32'
  };

  const roundedClass = rounded ? 'rounded-2xl' : '';

  return (
    <div className={`inline-flex items-center justify-center overflow-hidden ${roundedClass} ${sizeClasses[size]} ${className}`}>
      <img 
        src="/logo.png" 
        alt={process.env.REACT_APP_NAME} 
        title={title}
        className="w-full h-full object-contain"
      />
    </div>
  );
};

export default Logo;