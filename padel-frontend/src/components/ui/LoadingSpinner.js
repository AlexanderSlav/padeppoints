import React from 'react';

const LoadingSpinner = ({ size = 'medium', message = 'Loading...' }) => {
  const sizeClasses = {
    small: { fontSize: '16px', padding: '20px' },
    medium: { fontSize: '32px', padding: '40px' },
    large: { fontSize: '48px', padding: '60px' }
  };

  const style = sizeClasses[size] || sizeClasses.medium;

  return (
    <div className="container">
      <div className="card">
        <div style={{ textAlign: 'center', padding: style.padding }}>
          <div style={{ fontSize: style.fontSize, marginBottom: '16px' }}>🔄</div>
          <p>{message}</p>
        </div>
      </div>
    </div>
  );
};

export default LoadingSpinner;