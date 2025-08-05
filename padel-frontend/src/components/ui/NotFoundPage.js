import React from 'react';

const NotFoundPage = () => {
  return (
    <div className="container">
      <div className="card">
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>❌</div>
          <h2>Page Not Found</h2>
          <p style={{ color: '#718096' }}>The page you're looking for doesn't exist.</p>
          <div style={{ marginTop: '24px' }}>
            <a href="/dashboard" className="btn">
              Go to Dashboard
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotFoundPage;