import React from 'react';

const HeroIllustration = () => {
  return (
    <svg viewBox="0 0 800 600" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Background gradient */}
      <defs>
        <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#e8f0fe', stopOpacity: 1 }} />
          <stop offset="100%" style={{ stopColor: '#f8f9fa', stopOpacity: 1 }} />
        </linearGradient>
        <linearGradient id="chartGradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#1a73e8', stopOpacity: 0.8 }} />
          <stop offset="100%" style={{ stopColor: '#1a73e8', stopOpacity: 0.2 }} />
        </linearGradient>
      </defs>
      
      {/* Background */}
      <rect width="800" height="600" fill="url(#bgGradient)" />
      
      {/* Dashboard mockup */}
      <g transform="translate(100, 80)">
        {/* Main dashboard card */}
        <rect x="0" y="0" width="600" height="440" rx="12" fill="white" stroke="#dadce0" strokeWidth="2" />
        
        {/* Header bar */}
        <rect x="0" y="0" width="600" height="60" rx="12" fill="#1a73e8" />
        <text x="30" y="38" fill="white" fontSize="20" fontWeight="bold">Market Stability Monitor</text>
        
        {/* MSI Score Card */}
        <rect x="30" y="90" width="260" height="140" rx="8" fill="#e8f0fe" />
        <text x="50" y="120" fill="#5f6368" fontSize="14" fontWeight="500">MARKET STABILITY INDEX</text>
        <text x="50" y="170" fill="#1a73e8" fontSize="56" fontWeight="bold">87</text>
        <text x="50" y="200" fill="#34a853" fontSize="16" fontWeight="500">STABLE</text>
        
        {/* Trust Score */}
        <rect x="310" y="90" width="260" height="140" rx="8" fill="#f8f9fa" />
        <text x="330" y="120" fill="#5f6368" fontSize="14" fontWeight="500">TRUST SCORE</text>
        <text x="330" y="170" fill="#34a853" fontSize="56" fontWeight="bold">92</text>
        <text x="330" y="200" fill="#5f6368" fontSize="16">SAFE</text>
        
        {/* Chart area */}
        <rect x="30" y="260" width="540" height="150" rx="8" fill="#f8f9fa" />
        
        {/* Line chart */}
        <polyline
          points="50,350 100,340 150,360 200,330 250,345 300,320 350,340 400,310 450,330 500,315 550,325"
          fill="url(#chartGradient)"
          stroke="#1a73e8"
          strokeWidth="3"
        />
        
        {/* Anomaly markers */}
        <circle cx="200" cy="330" r="6" fill="#ea4335" />
        <circle cx="400" cy="310" r="6" fill="#ea4335" />
        
        {/* Chart grid lines */}
        <line x1="50" y1="280" x2="550" y2="280" stroke="#dadce0" strokeWidth="1" opacity="0.5" />
        <line x1="50" y1="320" x2="550" y2="320" stroke="#dadce0" strokeWidth="1" opacity="0.5" />
        <line x1="50" y1="360" x2="550" y2="360" stroke="#dadce0" strokeWidth="1" opacity="0.5" />
      </g>
      
      {/* Floating elements */}
      <g opacity="0.6">
        {/* Shield icon */}
        <circle cx="680" cy="150" r="40" fill="#34a853" opacity="0.2" />
        <text x="660" y="165" fontSize="40">🛡️</text>
        
        {/* Alert icon */}
        <circle cx="120" cy="480" r="35" fill="#ea4335" opacity="0.2" />
        <text x="103" y="493" fontSize="35">⚠️</text>
        
        {/* Lock icon */}
        <circle cx="720" cy="480" r="35" fill="#1a73e8" opacity="0.2" />
        <text x="703" y="493" fontSize="35">🔒</text>
      </g>
    </svg>
  );
};

export default HeroIllustration;
