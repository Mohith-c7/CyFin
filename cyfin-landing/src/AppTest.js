import React from 'react';

function AppTest() {
  return (
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: 'white',
      fontFamily: 'Arial, sans-serif'
    }}>
      <div style={{ textAlign: 'center', padding: '2rem' }}>
        <h1 style={{ fontSize: '4rem', marginBottom: '1rem' }}>🚀 CyFin</h1>
        <p style={{ fontSize: '1.5rem', marginBottom: '2rem' }}>
          Market Stability Monitoring Platform
        </p>
        <a 
          href="http://localhost:8502" 
          target="_blank" 
          rel="noopener noreferrer"
          style={{
            display: 'inline-block',
            padding: '1rem 2rem',
            background: 'white',
            color: '#667eea',
            textDecoration: 'none',
            borderRadius: '50px',
            fontWeight: 'bold',
            fontSize: '1.2rem'
          }}
        >
          Launch Dashboard →
        </a>
      </div>
    </div>
  );
}

export default AppTest;
