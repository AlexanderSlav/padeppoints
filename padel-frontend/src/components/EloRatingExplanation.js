import React, { useState } from 'react';

const EloRatingExplanation = () => {
  const [isExpanded, setIsExpanded] = useState(false);

  const ratingRanges = [
    { min: 1000, max: 1099, level: 'Beginner', color: '#48bb78', playtomic: '1.0', description: 'No experience, just starting to play' },
    { min: 1100, max: 1199, level: 'Novice', color: '#68d391', playtomic: '2.0', description: 'Consistent at a low pace' },
    { min: 1200, max: 1299, level: 'Improver', color: '#9ae6b4', playtomic: '2.5', description: 'Consistent at medium pace, shots lack direction' },
    { min: 1300, max: 1399, level: 'Weak Intermediate', color: '#f6e05e', playtomic: '3.0', description: 'Building confidence with shorts, consistent at medium pace' },
    { min: 1400, max: 1499, level: 'Intermediate', color: '#f6ad55', playtomic: '3.5', description: 'Has control and pace, previous racquet skills' },
    { min: 1500, max: 1599, level: 'Strong Intermediate', color: '#ed8936', playtomic: '4.0', description: 'Experience constructing padel points, consistent player' },
    { min: 1600, max: 1699, level: 'Weak Advanced', color: '#fc8181', playtomic: '4.5', description: 'Resourceful - executing winners, ability to force errors' },
    { min: 1700, max: 1799, level: 'Advanced', color: '#f56565', playtomic: '5.0', description: 'Experience competing at tournament level' },
    { min: 1800, max: 1899, level: 'Strong Advanced', color: '#e53e3e', playtomic: '5.5', description: 'Top nationally ranked player, regular tournament competitor' },
    { min: 1900, max: 1999, level: 'Weak Expert', color: '#c53030', playtomic: '6.0', description: 'Semi-professional, World ranking outside top 250' },
    { min: 2000, max: 9999, level: 'Expert', color: '#9b2c2c', playtomic: '6.5+', description: 'Professional player, World ranking potential' }
  ];

  const getRatingColor = (rating) => {
    const range = ratingRanges.find(r => rating >= r.min && rating <= r.max);
    return range ? range.color : '#718096';
  };

  return (
    <div style={{
      backgroundColor: 'white',
      borderRadius: '16px',
      padding: '24px',
      marginTop: '24px',
      boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
    }}>
      <div 
        onClick={() => setIsExpanded(!isExpanded)}
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          cursor: 'pointer',
          marginBottom: isExpanded ? '24px' : 0
        }}
      >
        <h3 style={{
          margin: 0,
          fontSize: '18px',
          fontWeight: 'bold',
          color: '#1a202c',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          📊 Understanding ELO Ratings
        </h3>
        <div style={{
          transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
          transition: 'transform 0.3s ease',
          fontSize: '20px'
        }}>
          ▼
        </div>
      </div>

      {isExpanded && (
        <div>
          {/* How ELO Works Section */}
          <div style={{ marginBottom: '32px' }}>
            <h4 style={{ color: '#2d3748', fontSize: '16px', fontWeight: '600', marginBottom: '12px' }}>
              How ELO Rating Works
            </h4>
            <p style={{ color: '#4a5568', fontSize: '14px', lineHeight: '1.6', marginBottom: '16px' }}>
              The ELO rating system is a method for calculating the relative skill levels of players. 
              Originally developed for chess, it's now widely used in competitive sports including padel.
            </p>
            <div style={{ backgroundColor: '#f7fafc', padding: '16px', borderRadius: '8px', marginBottom: '16px' }}>
              <ul style={{ margin: 0, paddingLeft: '20px', color: '#4a5568', fontSize: '14px', lineHeight: '1.8' }}>
                <li><strong>Starting Rating:</strong> Every player begins at 1000 ELO</li>
                <li><strong>Dynamic Adjustments:</strong> Ratings change based on match results and opponent strength</li>
                <li><strong>Win Expectancy:</strong> Beating higher-rated opponents gives more points</li>
                <li><strong>Loss Impact:</strong> Losing to lower-rated opponents costs more points</li>
                <li><strong>Tournament Finals:</strong> Your rating updates after completing a tournament</li>
              </ul>
            </div>
          </div>

          {/* Rating Distribution Curve */}
          <div style={{ marginBottom: '32px' }}>
            <h4 style={{ color: '#2d3748', fontSize: '16px', fontWeight: '600', marginBottom: '12px' }}>
              Rating Distribution
            </h4>
            <div style={{ 
              background: 'linear-gradient(90deg, #48bb78 0%, #f6e05e 35%, #ed8936 65%, #e53e3e 100%)',
              height: '80px',
              borderRadius: '8px',
              position: 'relative',
              marginBottom: '8px'
            }}>
              {/* Bell curve shape overlay */}
              <svg 
                width="100%" 
                height="80" 
                style={{ position: 'absolute', top: 0, left: 0 }}
                viewBox="0 0 400 80"
                preserveAspectRatio="none"
              >
                <path
                  d="M 0,80 Q 100,20 200,10 T 400,80"
                  fill="rgba(255,255,255,0.3)"
                  stroke="white"
                  strokeWidth="2"
                />
              </svg>
              {/* Rating markers */}
              <div style={{ 
                position: 'absolute', 
                bottom: '-20px', 
                width: '100%', 
                display: 'flex', 
                justifyContent: 'space-between',
                fontSize: '12px',
                color: '#718096'
              }}>
                <span>1000</span>
                <span>1300</span>
                <span>1500</span>
                <span>1700</span>
                <span>2000</span>
              </div>
            </div>
            <p style={{ 
              color: '#718096', 
              fontSize: '12px', 
              textAlign: 'center', 
              marginTop: '24px',
              fontStyle: 'italic'
            }}>
              Most players fall between 1300-1700 ELO
            </p>
          </div>

          {/* Rating Scale Table */}
          <div style={{ marginBottom: '32px' }}>
            <h4 style={{ color: '#2d3748', fontSize: '16px', fontWeight: '600', marginBottom: '12px' }}>
              Rating Scale & Playtomic Levels
            </h4>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f7fafc' }}>
                    <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #e2e8f0' }}>ELO Range</th>
                    <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #e2e8f0' }}>Skill Level</th>
                    <th style={{ padding: '12px', textAlign: 'center', borderBottom: '2px solid #e2e8f0' }}>Playtomic</th>
                    <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #e2e8f0' }}>Description</th>
                  </tr>
                </thead>
                <tbody>
                  {ratingRanges.map((range, index) => (
                    <tr key={index} style={{ borderBottom: '1px solid #e2e8f0' }}>
                      <td style={{ padding: '12px' }}>
                        <span style={{
                          backgroundColor: range.color,
                          color: 'white',
                          padding: '4px 8px',
                          borderRadius: '4px',
                          fontWeight: '600',
                          fontSize: '12px'
                        }}>
                          {range.min}-{range.max === 9999 ? '2000+' : range.max}
                        </span>
                      </td>
                      <td style={{ padding: '12px', fontWeight: '500', color: '#2d3748' }}>
                        {range.level}
                      </td>
                      <td style={{ 
                        padding: '12px', 
                        textAlign: 'center',
                        fontWeight: '600',
                        color: '#805ad5'
                      }}>
                        {range.playtomic}
                      </td>
                      <td style={{ padding: '12px', color: '#4a5568', fontSize: '13px' }}>
                        {range.description}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Playtomic Division Mapping */}
          <div>
            <h4 style={{ color: '#2d3748', fontSize: '16px', fontWeight: '600', marginBottom: '12px' }}>
              Playtomic Division Mapping
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
              <div style={{ 
                backgroundColor: '#f0fff4', 
                padding: '12px', 
                borderRadius: '8px',
                border: '1px solid #9ae6b4'
              }}>
                <div style={{ fontWeight: '600', color: '#22543d', marginBottom: '4px' }}>Division C</div>
                <div style={{ fontSize: '12px', color: '#2f855a' }}>Levels 1.0 - 3.0</div>
                <div style={{ fontSize: '12px', color: '#68d391', marginTop: '4px' }}>ELO 1000-1399</div>
              </div>
              <div style={{ 
                backgroundColor: '#fffaf0', 
                padding: '12px', 
                borderRadius: '8px',
                border: '1px solid #fbd38d'
              }}>
                <div style={{ fontWeight: '600', color: '#744210', marginBottom: '4px' }}>Division B</div>
                <div style={{ fontSize: '12px', color: '#975a16' }}>Levels 3.5 - 5.0</div>
                <div style={{ fontSize: '12px', color: '#f6ad55', marginTop: '4px' }}>ELO 1400-1799</div>
              </div>
              <div style={{ 
                backgroundColor: '#fff5f5', 
                padding: '12px', 
                borderRadius: '8px',
                border: '1px solid #feb2b2'
              }}>
                <div style={{ fontWeight: '600', color: '#742a2a', marginBottom: '4px' }}>Division A</div>
                <div style={{ fontSize: '12px', color: '#9b2c2c' }}>Levels 5.5 - 7.0</div>
                <div style={{ fontSize: '12px', color: '#fc8181', marginTop: '4px' }}>ELO 1800+</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EloRatingExplanation;