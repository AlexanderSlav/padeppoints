import React, { useState } from 'react';
import { ratingRanges } from '../config/eloRatings';

const InfoSection = () => {
  const [expandedSection, setExpandedSection] = useState(null);

  const toggleSection = (section) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  return (
    <div style={{
      backgroundColor: 'white',
      borderRadius: '16px',
      padding: '32px',
      maxWidth: '1200px',
      margin: '24px auto',
      boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
    }}>
      <h2 style={{
        fontSize: '24px',
        fontWeight: '600',
        color: '#111827',
        marginBottom: '24px',
        textAlign: 'center'
      }}>
        Tournament Information
      </h2>

      {/* How ELO Works */}
      <div style={{ marginBottom: '24px' }}>
        <div 
          onClick={() => toggleSection('elo')}
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            cursor: 'pointer',
            padding: '16px',
            backgroundColor: '#f9fafb',
            borderRadius: '8px',
            marginBottom: expandedSection === 'elo' ? '16px' : 0
          }}
        >
          <h3 style={{
            margin: 0,
            fontSize: '18px',
            fontWeight: '600',
            color: '#111827'
          }}>
            Understanding ELO Ratings
          </h3>
          <div style={{
            transform: expandedSection === 'elo' ? 'rotate(180deg)' : 'rotate(0deg)',
            transition: 'transform 0.3s ease',
            color: '#6b7280'
          }}>
            ▼
          </div>
        </div>

        {expandedSection === 'elo' && (
          <div style={{ padding: '0 16px' }}>
            <p style={{ color: '#4b5563', fontSize: '14px', lineHeight: '1.6', marginBottom: '16px' }}>
              The ELO rating system is a method for calculating the relative skill levels of players. 
              Originally developed for chess, it's now widely used in competitive sports including padel.
            </p>
            
            <div style={{ backgroundColor: '#f9fafb', padding: '16px', borderRadius: '8px', marginBottom: '20px' }}>
              <h4 style={{ color: '#374151', fontSize: '14px', fontWeight: '600', marginBottom: '12px' }}>
                Key Points:
              </h4>
              <ul style={{ margin: 0, paddingLeft: '20px', color: '#4b5563', fontSize: '14px', lineHeight: '1.8' }}>
                <li>Every player begins at 1000 ELO</li>
                <li>Ratings change based on match results and opponent strength</li>
                <li>Beating higher-rated opponents gives more points</li>
                <li>Losing to lower-rated opponents costs more points</li>
                <li>Your rating updates after completing a tournament</li>
              </ul>
            </div>

            {/* Rating Scale Table */}
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f9fafb' }}>
                    <th style={{ padding: '10px', textAlign: 'left', borderBottom: '2px solid #e5e7eb', color: '#374151' }}>ELO Range</th>
                    <th style={{ padding: '10px', textAlign: 'left', borderBottom: '2px solid #e5e7eb', color: '#374151' }}>Skill Level</th>
                    <th style={{ padding: '10px', textAlign: 'center', borderBottom: '2px solid #e5e7eb', color: '#374151' }}>Playtomic</th>
                    <th style={{ padding: '10px', textAlign: 'left', borderBottom: '2px solid #e5e7eb', color: '#374151' }}>Description</th>
                  </tr>
                </thead>
                <tbody>
                  {ratingRanges.map((range, index) => (
                    <tr key={index} style={{ borderBottom: '1px solid #e5e7eb' }}>
                      <td style={{ padding: '10px' }}>
                        <span style={{
                          backgroundColor: range.color,
                          color: 'white',
                          padding: '2px 6px',
                          borderRadius: '4px',
                          fontWeight: '500',
                          fontSize: '12px'
                        }}>
                          {range.min}-{range.max === 9999 ? '2000+' : range.max}
                        </span>
                      </td>
                      <td style={{ padding: '10px', fontWeight: '500', color: '#374151' }}>
                        {range.level}
                      </td>
                      <td style={{ 
                        padding: '10px', 
                        textAlign: 'center',
                        fontWeight: '600',
                        color: '#6366f1'
                      }}>
                        {range.playtomic}
                      </td>
                      <td style={{ padding: '10px', color: '#6b7280', fontSize: '12px' }}>
                        {range.description}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Tournament Formats */}
      <div style={{ marginBottom: '24px' }}>
        <div 
          onClick={() => toggleSection('formats')}
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            cursor: 'pointer',
            padding: '16px',
            backgroundColor: '#f9fafb',
            borderRadius: '8px',
            marginBottom: expandedSection === 'formats' ? '16px' : 0
          }}
        >
          <h3 style={{
            margin: 0,
            fontSize: '18px',
            fontWeight: '600',
            color: '#111827'
          }}>
            Tournament Formats
          </h3>
          <div style={{
            transform: expandedSection === 'formats' ? 'rotate(180deg)' : 'rotate(0deg)',
            transition: 'transform 0.3s ease',
            color: '#6b7280'
          }}>
            ▼
          </div>
        </div>

        {expandedSection === 'formats' && (
          <div style={{ padding: '0 16px' }}>
            <div style={{ marginBottom: '20px' }}>
              <h4 style={{ color: '#374151', fontSize: '16px', fontWeight: '600', marginBottom: '8px' }}>
                Americano Format
              </h4>
              <p style={{ color: '#4b5563', fontSize: '14px', lineHeight: '1.6', marginBottom: '12px' }}>
                A round-robin format where players change partners each round, competing to accumulate the most points individually.
              </p>
              <ul style={{ margin: 0, paddingLeft: '20px', color: '#4b5563', fontSize: '14px', lineHeight: '1.8' }}>
                <li>Players are paired with different partners each round</li>
                <li>Individual points are tracked across all matches</li>
                <li>Winners are determined by total points accumulated</li>
                <li>Promotes fair play and social interaction</li>
              </ul>
            </div>

            <div>
              <h4 style={{ color: '#374151', fontSize: '16px', fontWeight: '600', marginBottom: '8px' }}>
                Mexicano Format (Coming Soon)
              </h4>
              <p style={{ color: '#4b5563', fontSize: '14px', lineHeight: '1.6' }}>
                A dynamic format where pairings are determined based on current standings, ensuring competitive matches throughout.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* How to Join */}
      <div>
        <div 
          onClick={() => toggleSection('join')}
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            cursor: 'pointer',
            padding: '16px',
            backgroundColor: '#f9fafb',
            borderRadius: '8px',
            marginBottom: expandedSection === 'join' ? '16px' : 0
          }}
        >
          <h3 style={{
            margin: 0,
            fontSize: '18px',
            fontWeight: '600',
            color: '#111827'
          }}>
            How to Join a Tournament
          </h3>
          <div style={{
            transform: expandedSection === 'join' ? 'rotate(180deg)' : 'rotate(0deg)',
            transition: 'transform 0.3s ease',
            color: '#6b7280'
          }}>
            ▼
          </div>
        </div>

        {expandedSection === 'join' && (
          <div style={{ padding: '0 16px' }}>
            <ol style={{ margin: 0, paddingLeft: '20px', color: '#4b5563', fontSize: '14px', lineHeight: '1.8' }}>
              <li>Browse available tournaments in the Discover section</li>
              <li>Check tournament details including format, location, and entry fee</li>
              <li>Click "Quick Join" if the tournament is still accepting players</li>
              <li>Wait for the tournament to start (minimum 4 players required)</li>
              <li>Show up at the venue on time and enjoy your matches!</li>
            </ol>
          </div>
        )}
      </div>
    </div>
  );
};

export default InfoSection;