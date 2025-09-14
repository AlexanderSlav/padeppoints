import React from 'react';
import { ratingRanges } from '../config/eloRatings';

const EloInfoPopup = ({ isOpen, onClose, currentRating }) => {
  if (!isOpen) return null;

  const currentRange = ratingRanges.find(r => currentRating >= r.min && currentRating <= r.max);

  return (
    <>
      {/* Backdrop with blur */}
      <div
        onClick={onClose}
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          backdropFilter: 'blur(8px)',
          WebkitBackdropFilter: 'blur(8px)',
          zIndex: 9998,
          animation: 'fadeIn 0.2s ease-out'
        }}
      />

      {/* Popup Modal */}
      <div style={{
        position: 'fixed',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        backgroundColor: 'white',
        borderRadius: '24px',
        padding: '32px',
        maxWidth: '500px',
        width: '90%',
        maxHeight: '80vh',
        overflowY: 'auto',
        boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
        zIndex: 9999,
        animation: 'slideUp 0.3s ease-out'
      }}>
        {/* Header with Icon */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          marginBottom: '24px'
        }}>
          <div style={{
            width: '48px',
            height: '48px',
            borderRadius: '12px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '24px'
          }}>
            🏆
          </div>
          <div>
            <h2 style={{
              margin: 0,
              fontSize: '24px',
              fontWeight: '700',
              color: '#1a202c'
            }}>
              ELO Rating System
            </h2>
            <p style={{
              margin: '4px 0 0 0',
              fontSize: '14px',
              color: '#718096'
            }}>
              Level {currentRange?.playtomic || 'N/A'}
            </p>
          </div>
        </div>

        {/* Current Rating Display */}
        {currentRange && (
          <div style={{
            background: 'linear-gradient(135deg, #f6f8fb 0%, #e9ecef 100%)',
            borderRadius: '16px',
            padding: '20px',
            marginBottom: '24px',
            textAlign: 'center'
          }}>
            <div style={{
              fontSize: '36px',
              fontWeight: '700',
              color: '#1a202c',
              marginBottom: '8px'
            }}>
              {currentRating}
            </div>
            <div style={{
              display: 'inline-block',
              backgroundColor: currentRange.color,
              color: 'white',
              padding: '6px 16px',
              borderRadius: '20px',
              fontSize: '14px',
              fontWeight: '600',
              marginBottom: '12px'
            }}>
              {currentRange.level}
            </div>
            <p style={{
              margin: 0,
              fontSize: '14px',
              color: '#4a5568',
              lineHeight: '1.5'
            }}>
              {currentRange.description}
            </p>
          </div>
        )}

        {/* Info Text */}
        <div style={{ marginBottom: '24px' }}>
          <p style={{
            fontSize: '15px',
            color: '#4a5568',
            lineHeight: '1.6',
            margin: '0 0 16px 0'
          }}>
            The ELO rating system calculates your skill level based on match results.
            Your rating will increase when you win and decrease when you lose, with
            the amount depending on your opponent's rating.
          </p>

          <div style={{
            background: '#f7fafc',
            borderRadius: '12px',
            padding: '16px',
            border: '1px solid #e2e8f0'
          }}>
            <h4 style={{
              margin: '0 0 12px 0',
              fontSize: '14px',
              fontWeight: '600',
              color: '#2d3748'
            }}>
              How it works:
            </h4>
            <ul style={{
              margin: 0,
              paddingLeft: '20px',
              fontSize: '14px',
              color: '#4a5568',
              lineHeight: '1.8'
            }}>
              <li>Win against stronger opponents = More points gained</li>
              <li>Win against weaker opponents = Fewer points gained</li>
              <li>Lose to weaker opponents = More points lost</li>
              <li>Lose to stronger opponents = Fewer points lost</li>
            </ul>
          </div>
        </div>

        {/* Rating Scale Preview */}
        <div style={{ marginBottom: '24px' }}>
          <h4 style={{
            margin: '0 0 16px 0',
            fontSize: '16px',
            fontWeight: '600',
            color: '#2d3748'
          }}>
            Rating Scale
          </h4>
          <div style={{
            display: 'grid',
            gap: '8px'
          }}>
            {ratingRanges.slice(0, 6).map((range, index) => (
              <div
                key={index}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '8px',
                  borderRadius: '8px',
                  backgroundColor: currentRange === range ? '#f0f4f8' : 'transparent',
                  border: currentRange === range ? '2px solid #cbd5e0' : '2px solid transparent'
                }}
              >
                <div style={{
                  width: '80px',
                  fontSize: '12px',
                  fontWeight: '600',
                  color: '#4a5568'
                }}>
                  {range.min}-{range.max === 9999 ? '2000+' : range.max}
                </div>
                <div style={{
                  flex: 1,
                  height: '24px',
                  backgroundColor: range.color,
                  borderRadius: '4px',
                  display: 'flex',
                  alignItems: 'center',
                  paddingLeft: '8px'
                }}>
                  <span style={{
                    color: 'white',
                    fontSize: '12px',
                    fontWeight: '500'
                  }}>
                    {range.level}
                  </span>
                </div>
                <div style={{
                  fontSize: '12px',
                  color: '#718096',
                  fontWeight: '500'
                }}>
                  {range.playtomic}
                </div>
              </div>
            ))}
          </div>
          {ratingRanges.length > 6 && (
            <p style={{
              margin: '12px 0 0 0',
              fontSize: '12px',
              color: '#718096',
              textAlign: 'center'
            }}>
              + {ratingRanges.length - 6} more levels
            </p>
          )}
        </div>

        {/* Action Button */}
        <button
          onClick={onClose}
          style={{
            width: '100%',
            padding: '14px',
            backgroundColor: '#4299e1',
            color: 'white',
            border: 'none',
            borderRadius: '12px',
            fontSize: '16px',
            fontWeight: '600',
            cursor: 'pointer',
            transition: 'background-color 0.2s'
          }}
          onMouseEnter={(e) => e.target.style.backgroundColor = '#3182ce'}
          onMouseLeave={(e) => e.target.style.backgroundColor = '#4299e1'}
        >
          Got it
        </button>
      </div>

      {/* Animation Styles */}
      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translate(-50%, -40%);
          }
          to {
            opacity: 1;
            transform: translate(-50%, -50%);
          }
        }
      `}</style>
    </>
  );
};

export default EloInfoPopup;