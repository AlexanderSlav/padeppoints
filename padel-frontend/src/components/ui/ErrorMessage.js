import React from 'react';

const ErrorMessage = ({ 
  message, 
  title = 'Error', 
  onRetry = null, 
  showIcon = true,
  type = 'error' // 'error', 'warning', 'info'
}) => {
  const getIcon = () => {
    switch (type) {
      case 'warning':
        return '⚠️';
      case 'info':
        return 'ℹ️';
      default:
        return '❌';
    }
  };

  const getStyles = () => {
    const baseStyles = {
      textAlign: 'center',
      padding: '40px',
    };

    switch (type) {
      case 'warning':
        return { ...baseStyles, borderLeft: '4px solid #f59e0b' };
      case 'info':
        return { ...baseStyles, borderLeft: '4px solid #3b82f6' };
      default:
        return { ...baseStyles, borderLeft: '4px solid #ef4444' };
    }
  };

  return (
    <div className="container">
      <div className="card">
        <div style={getStyles()}>
          {showIcon && (
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>
              {getIcon()}
            </div>
          )}
          <h2>{title}</h2>
          <p style={{ color: '#718096', marginBottom: '24px' }}>{message}</p>
          {onRetry && (
            <button onClick={onRetry} className="btn">
              Try Again
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ErrorMessage;