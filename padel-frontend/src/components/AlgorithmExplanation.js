import React from 'react';

const AlgorithmExplanation = () => {
  return (
    <div style={{ fontSize: '14px', color: '#4a5568', lineHeight: '1.8' }}>
      <div style={{ marginBottom: '16px' }}>
        <strong style={{ color: '#2d3748' }}>🎯 Goal:</strong> Find the maximum points per match that fits within your time constraint.
      </div>

      <div style={{ marginBottom: '16px' }}>
        <strong style={{ color: '#2d3748' }}>📐 Step 1: Tournament Structure</strong>
        <ul style={{ marginLeft: '20px', marginTop: '8px' }}>
          <li>Total Rounds = Number of Players - 1</li>
          <li>Matches per Round = Players ÷ 4</li>
          <li>Total Matches = Rounds × Matches per Round</li>
        </ul>
      </div>

      <div style={{ marginBottom: '16px' }}>
        <strong style={{ color: '#2d3748' }}>⏱️ Step 2: Time Calculation</strong>
        <div style={{ 
          backgroundColor: '#edf2f7', 
          padding: '10px', 
          borderRadius: '4px', 
          marginTop: '8px',
          fontFamily: 'monospace',
          fontSize: '13px'
        }}>
          Time per Match = (Points × Seconds per Rally) + Rest Time<br/>
          Total Time = (Total Matches × Time per Match) ÷ Courts
        </div>
      </div>

      <div style={{ marginBottom: '16px' }}>
        <strong style={{ color: '#2d3748' }}>🔄 Step 3: Find Maximum Points</strong>
        <p style={{ marginTop: '8px' }}>
          The algorithm tests point values from high to low (48, 44, 40, 36, 32, 28, 24, 20, 16) 
          and returns the highest value that fits within your time limit.
        </p>
      </div>

      <div style={{ marginBottom: '16px' }}>
        <strong style={{ color: '#2d3748' }}>📊 Example: 8 Players, 2 Courts, 2 Hours</strong>
        <ExampleTable />
        <p style={{ marginTop: '8px', fontSize: '13px', color: '#718096' }}>
          Result: 36 points per match (maximum that fits)
        </p>
      </div>

      <div style={{ marginBottom: '16px' }}>
        <strong style={{ color: '#2d3748' }}>⚡ Efficiency Calculation</strong>
        <ul style={{ marginLeft: '20px', marginTop: '8px' }}>
          <li><strong>If tournament fits:</strong> Efficiency = Time Used ÷ Available Time</li>
          <li><strong>If partial:</strong> Efficiency = 100% (using all available time)</li>
        </ul>
      </div>

      <ProTips />
    </div>
  );
};

const ExampleTable = () => (
  <table style={{ 
    width: '100%', 
    marginTop: '8px',
    borderCollapse: 'collapse',
    fontSize: '13px'
  }}>
    <thead>
      <tr style={{ backgroundColor: '#e2e8f0' }}>
        <th style={{ padding: '8px', textAlign: 'left', borderBottom: '2px solid #cbd5e0' }}>Points</th>
        <th style={{ padding: '8px', textAlign: 'left', borderBottom: '2px solid #cbd5e0' }}>Time Needed</th>
        <th style={{ padding: '8px', textAlign: 'left', borderBottom: '2px solid #cbd5e0' }}>Fits in 2h?</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td style={{ padding: '8px', borderBottom: '1px solid #e2e8f0' }}>48</td>
        <td style={{ padding: '8px', borderBottom: '1px solid #e2e8f0' }}>147 min</td>
        <td style={{ padding: '8px', borderBottom: '1px solid #e2e8f0' }}>❌ No</td>
      </tr>
      <tr>
        <td style={{ padding: '8px', borderBottom: '1px solid #e2e8f0' }}>40</td>
        <td style={{ padding: '8px', borderBottom: '1px solid #e2e8f0' }}>124 min</td>
        <td style={{ padding: '8px', borderBottom: '1px solid #e2e8f0' }}>❌ No</td>
      </tr>
      <tr style={{ backgroundColor: '#c6f6d5' }}>
        <td style={{ padding: '8px', borderBottom: '1px solid #e2e8f0', fontWeight: 'bold' }}>36</td>
        <td style={{ padding: '8px', borderBottom: '1px solid #e2e8f0', fontWeight: 'bold' }}>112 min</td>
        <td style={{ padding: '8px', borderBottom: '1px solid #e2e8f0', fontWeight: 'bold' }}>✅ Yes!</td>
      </tr>
    </tbody>
  </table>
);

const ProTips = () => (
  <div style={{
    backgroundColor: '#e6fffa',
    padding: '12px',
    borderRadius: '6px',
    marginTop: '16px'
  }}>
    <strong style={{ color: '#2d3748' }}>💡 Pro Tips:</strong>
    <ul style={{ marginLeft: '20px', marginTop: '8px', marginBottom: 0 }}>
      <li>Leave "Points per Match" empty to find the maximum</li>
      <li>Adjust "Seconds per Rally" based on your playing style</li>
      <li>More courts = shorter tournament duration</li>
      <li>Players must be divisible by 4 for Americano format</li>
    </ul>
  </div>
);

export default AlgorithmExplanation;