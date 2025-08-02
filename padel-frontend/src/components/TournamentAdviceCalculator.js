import React, { useState } from 'react';
import { tournamentAPI } from '../services/api';
import AlgorithmExplanation from './AlgorithmExplanation';

const TournamentAdviceCalculator = ({ isModal = true, onClose = null }) => {
  const [adviceParams, setAdviceParams] = useState({
    courts: '',
    players: '',
    hours: '',
    secondsPerPoint: '25',  // Default 25 seconds per rally
    restSeconds: '60',  // Default 60 seconds rest between matches
    pointsPerMatch: ''  // Empty by default to calculate optimal
  });
  const [adviceResult, setAdviceResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showExplanation, setShowExplanation] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setAdviceParams(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const calculateOptimalPoints = async () => {
    const courts = parseInt(adviceParams.courts) || 0;
    const players = parseInt(adviceParams.players) || 0;
    const hours = parseFloat(adviceParams.hours) || 0;
    const secondsPerPoint = parseInt(adviceParams.secondsPerPoint) || 25;
    const restSeconds = parseInt(adviceParams.restSeconds) || 60;
    const pointsPerMatch = adviceParams.pointsPerMatch ? parseInt(adviceParams.pointsPerMatch) : null;
    
    // Client-side validation
    if (courts <= 0 || players < 4 || hours <= 0 || secondsPerPoint < 10) {
      setAdviceResult({
        error: "Please enter valid values: Courts ≥ 1, Players ≥ 4, Hours > 0, Seconds per rally ≥ 10"
      });
      return;
    }

    if (pointsPerMatch !== null && pointsPerMatch <= 0) {
      setAdviceResult({
        error: "Points per Match must be greater than 0 if provided"
      });
      return;
    }

    if (players % 4 !== 0) {
      setAdviceResult({
        error: "Number of players must be divisible by 4 for Americano format (e.g., 4, 8, 12, 16, 20, 24)"
      });
      return;
    }
    
    setLoading(true);
    try {
      // Call the comprehensive backend endpoint
      const data = await tournamentAPI.getTournamentPlanningAdvice({
        players,
        courts,
        hours,
        secondsPerPoint,
        restSeconds,
        pointsPerMatch,
        system: 'AMERICANO'
      });
      
      // Transform backend response to frontend format
      setAdviceResult({
        // From backend structure
        maxRounds: data.tournament_structure.completable_rounds,
        totalRounds: data.tournament_structure.total_rounds,
        timePerRound: Math.round(data.time_analysis.minutes_per_round),
        totalOptimalPoints: data.points_analysis.achievable_points,
        pointsPerMatch: data.points_analysis.points_per_match,
        matchesPerRound: data.tournament_structure.matches_per_round,
        totalMatches: data.tournament_structure.completable_matches,
        estimatedTime: Math.round(data.time_analysis.actual_time_used),
        recommendation: data.recommendation,
        efficiency: data.time_analysis.efficiency_percentage,
        wasOptimalCalculated: data.input.was_calculated,
        secondsPerPoint: data.input.seconds_per_point,
        restSeconds: data.input.rest_seconds
      });
    } catch (err) {
      console.error('Failed to calculate advice:', err);
      setAdviceResult({
        error: err.response?.data?.detail || "Failed to calculate tournament estimation. Please check your inputs and try again."
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    calculateOptimalPoints();
  };

  const content = (
    <div>
      <h3 style={{ fontSize: '20px', fontWeight: 'bold', color: '#2d3748', marginBottom: '16px' }}>
        💡 Tournament Planning Advisor
      </h3>
      <p style={{ color: '#718096', marginBottom: '20px', fontSize: '14px' }}>
        Enter your available resources to get optimal tournament recommendations
      </p>
      
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#4a5568', marginBottom: '4px' }}>
            Number of Courts
          </label>
          <input
            type="number"
            id="courts"
            name="courts"
            value={adviceParams.courts}
            onChange={handleInputChange}
            placeholder="e.g., 2"
            min="1"
            style={{
              width: '100%',
              padding: '8px 12px',
              border: '2px solid #e2e8f0',
              borderRadius: '6px',
              fontSize: '14px'
            }}
          />
        </div>

        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#4a5568', marginBottom: '4px' }}>
            Number of Players
          </label>
          <input
            type="number"
            id="players"
            name="players"
            value={adviceParams.players}
            onChange={handleInputChange}
            placeholder="e.g., 8 (must be divisible by 4)"
            min="4"
            step="4"
            style={{
              width: '100%',
              padding: '8px 12px',
              border: '2px solid #e2e8f0',
              borderRadius: '6px',
              fontSize: '14px'
            }}
          />
        </div>

        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#4a5568', marginBottom: '4px' }}>
            Available Hours
          </label>
          <input
            type="number"
            id="hours"
            name="hours"
            step="0.5"
            value={adviceParams.hours}
            onChange={handleInputChange}
            placeholder="e.g., 3.5"
            min="0.5"
            style={{
              width: '100%',
              padding: '8px 12px',
              border: '2px solid #e2e8f0',
              borderRadius: '6px',
              fontSize: '14px'
            }}
          />
        </div>

        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#4a5568', marginBottom: '4px' }}>
            Seconds per Rally (Average)
          </label>
          <input
            type="number"
            id="secondsPerPoint"
            name="secondsPerPoint"
            value={adviceParams.secondsPerPoint}
            onChange={handleInputChange}
            placeholder="25"
            min="10"
            style={{
              width: '100%',
              padding: '8px 12px',
              border: '2px solid #e2e8f0',
              borderRadius: '6px',
              fontSize: '14px'
            }}
          />
          <p style={{ fontSize: '12px', color: '#718096', marginTop: '4px' }}>
            How many seconds does an average rally take? (minimum 10 seconds, default: 25)
          </p>
        </div>

        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#4a5568', marginBottom: '4px' }}>
            Rest Time Between Matches (Seconds)
          </label>
          <input
            type="number"
            id="restSeconds"
            name="restSeconds"
            value={adviceParams.restSeconds}
            onChange={handleInputChange}
            placeholder="60"
            min="0"
            style={{
              width: '100%',
              padding: '8px 12px',
              border: '2px solid #e2e8f0',
              borderRadius: '6px',
              fontSize: '14px'
            }}
          />
          <p style={{ fontSize: '12px', color: '#718096', marginTop: '4px' }}>
            Break time between matches in seconds (default: 60 seconds)
          </p>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#4a5568', marginBottom: '4px' }}>
            Points per Match (Optional)
          </label>
          <input
            type="number"
            id="pointsPerMatch"
            name="pointsPerMatch"
            value={adviceParams.pointsPerMatch}
            onChange={handleInputChange}
            placeholder="Leave empty for optimal calculation"
            min="1"
            style={{
              width: '100%',
              padding: '8px 12px',
              border: '2px solid #e2e8f0',
              borderRadius: '6px',
              fontSize: '14px'
            }}
          />
          <p style={{ fontSize: '12px', color: '#718096', marginTop: '4px' }}>
            If left empty, the system will calculate the maximum points that fit your time constraints
          </p>
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            width: '100%',
            padding: '12px 24px',
            backgroundColor: loading ? '#9ca3af' : '#4299e1',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontSize: '16px',
            fontWeight: '600',
            marginBottom: '20px'
          }}
        >
          {loading ? '🔄 Calculating...' : '📊 Get Planning Advice'}
        </button>
      </form>

      {/* Algorithm Explanation Dropdown */}
      <div style={{ marginBottom: '20px' }}>
        <button
          onClick={() => setShowExplanation(!showExplanation)}
          style={{
            width: '100%',
            padding: '12px 16px',
            backgroundColor: '#f7fafc',
            color: '#2d3748',
            border: '1px solid #e2e8f0',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '600',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            textAlign: 'left'
          }}
        >
          <span>🔍 How does the algorithm work?</span>
          <span style={{ fontSize: '18px' }}>{showExplanation ? '−' : '+'}</span>
        </button>
        
        {showExplanation && (
          <div style={{
            marginTop: '12px',
            padding: '20px',
            backgroundColor: '#f7fafc',
            borderRadius: '8px',
            border: '1px solid #e2e8f0'
          }}>
            <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#2d3748', marginBottom: '16px' }}>
              📊 Algorithm Explanation
            </h4>
            <AlgorithmExplanation />
          </div>
        )}
      </div>

      {loading && (
        <div style={{
          textAlign: 'center',
          padding: '20px',
          color: '#718096'
        }}>
          🔄 Calculating optimal setup...
        </div>
      )}

      {/* Results Display */}
      {adviceResult && !loading && (
        <div style={{
          backgroundColor: adviceResult.error ? '#fed7d7' : '#f0fff4',
          border: `1px solid ${adviceResult.error ? '#f56565' : '#9ae6b4'}`,
          borderRadius: '8px',
          padding: '16px',
          marginBottom: '16px'
        }}>
          {adviceResult.error ? (
            <div>
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#c53030', marginBottom: '8px' }}>
                ❌ Error
              </h4>
              <p style={{ color: '#c53030', margin: 0 }}>
                {adviceResult.error}
              </p>
            </div>
          ) : (
            <div>
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#2d3748', marginBottom: '8px' }}>
                📊 Tournament Setup Analysis
              </h4>
              <p style={{ color: '#4a5568', marginBottom: '12px', fontWeight: '500' }}>
                {adviceResult.recommendation}
              </p>
              
              {/* Key Metrics */}
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', 
                gap: '12px',
                marginBottom: '12px'
              }}>
                <div style={{ textAlign: 'center', backgroundColor: '#e6fffa', padding: '8px', borderRadius: '6px' }}>
                  <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#2d3748' }}>
                    {adviceResult.totalOptimalPoints}
                  </div>
                  <div style={{ fontSize: '12px', color: '#718096' }}>Total Points</div>
                </div>
                <div style={{ textAlign: 'center', backgroundColor: '#fef5e7', padding: '8px', borderRadius: '6px' }}>
                  <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#2d3748' }}>
                    {adviceResult.efficiency}%
                  </div>
                  <div style={{ fontSize: '12px', color: '#718096' }}>Time Efficiency</div>
                </div>
                <div style={{ textAlign: 'center', backgroundColor: '#f0f4ff', padding: '8px', borderRadius: '6px' }}>
                  <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#2d3748' }}>
                    {Math.floor(adviceResult.estimatedTime / 60)}h {adviceResult.estimatedTime % 60}m
                  </div>
                  <div style={{ fontSize: '12px', color: '#718096' }}>Est. Time</div>
                </div>
              </div>

              <div style={{ fontSize: '14px', color: '#718096', lineHeight: '1.5' }}>
                <div><strong>Rounds you can complete:</strong> {adviceResult.maxRounds} of {adviceResult.totalRounds}</div>
                <div><strong>Time per round:</strong> ~{adviceResult.timePerRound} minutes</div>
                <div><strong>Total matches:</strong> {adviceResult.totalMatches} ({adviceResult.matchesPerRound} per round)</div>
                <div><strong>Points per match:</strong> {adviceResult.pointsPerMatch}</div>
                <div><strong>Rally duration:</strong> {adviceResult.secondsPerPoint} seconds</div>
                <div><strong>Rest between matches:</strong> {adviceResult.restSeconds} seconds</div>
              </div>
            </div>
          )}
        </div>
      )}

      {isModal && (
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
          <button
            onClick={onClose}
            style={{
              padding: '8px 16px',
              backgroundColor: '#e2e8f0',
              color: '#4a5568',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600'
            }}
          >
            Close
          </button>
        </div>
      )}
    </div>
  );

  if (isModal) {
    return (
      <div 
        onClick={(e) => {
          if (e.target === e.currentTarget) {
            onClose();
          }
        }}
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}
      >
        <div 
          onClick={(e) => e.stopPropagation()}
          style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            padding: '24px',
            width: '90%',
            maxWidth: '600px',
            maxHeight: '90vh',
            overflowY: 'auto',
            boxShadow: '0 10px 25px rgba(0, 0, 0, 0.2)'
          }}
        >
          {content}
        </div>
      </div>
    );
  }

  return (
    <div style={{
      backgroundColor: 'white',
      borderRadius: '12px',
      padding: '24px',
      boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
      marginBottom: '24px'
    }}>
      {content}
    </div>
  );
};

export default TournamentAdviceCalculator;