import React from 'react';

const DashboardScreenshot = () => {
  return (
    <svg viewBox="0 0 600 400" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="dashGradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#1a73e8', stopOpacity: 0.8 }} />
          <stop offset="100%" style={{ stopColor: '#1a73e8', stopOpacity: 0.3 }} />
        </linearGradient>
      </defs>
      
      {/* Background */}
      <rect width="600" height="400" fill="#fafafa" />
      
      {/* Browser chrome */}
      <rect x="0" y="0" width="600" height="40" fill="#f1f3f4" />
      <circle cx="20" cy="20" r="6" fill="#ea4335" />
      <circle cx="40" cy="20" r="6" fill="#fbbc04" />
      <circle cx="60" cy="20" r="6" fill="#34a853" />
      
      {/* Dashboard content */}
      <rect x="20" y="60" width="560" height="320" rx="8" fill="white" stroke="#dadce0" strokeWidth="1" />
      
      {/* Header */}
      <rect x="20" y="60" width="560" height="50" rx="8" fill="#1a73e8" />
      <text x="40" y="90" fill="white" fontSize="18" fontWeight="bold">📊 Market Stability Monitor</text>
      
      {/* Metrics row */}
      <rect x="40" y="130" width="120" height="80" rx="6" fill="#e8f0fe" />
      <text x="50" y="155" fill="#5f6368" fontSize="11">MSI SCORE</text>
      <text x="50" y="190" fill="#1a73e8" fontSize="32" fontWeight="bold">87</text>
      
      <rect x="180" y="130" width="120" height="80" rx="6" fill="#e8f5e9" />
      <text x="190" y="155" fill="#5f6368" fontSize="11">TRUST</text>
      <text x="190" y="190" fill="#34a853" fontSize="32" fontWeight="bold">92</text>
      
      <rect x="320" y="130" width="120" height="80" rx="6" fill="#fef7e0" />
      <text x="330" y="155" fill="#5f6368" fontSize="11">ANOMALIES</text>
      <text x="330" y="190" fill="#f9ab00" fontSize="32" fontWeight="bold">3</text>
      
      <rect x="460" y="130" width="100" height="80" rx="6" fill="#fce8e6" />
      <text x="470" y="155" fill="#5f6368" fontSize="11">BLOCKED</text>
      <text x="470" y="190" fill="#ea4335" fontSize="32" fontWeight="bold">2</text>
      
      {/* Chart */}
      <rect x="40" y="230" width="520" height="130" rx="6" fill="white" stroke="#dadce0" strokeWidth="1" />
      <polyline
        points="60,320 100,310 140,330 180,300 220,315 260,290 300,310 340,280 380,300 420,285 460,295 500,280 540,290"
        fill="url(#dashGradient)"
        stroke="#1a73e8"
        strokeWidth="2"
      />
      <circle cx="180" cy="300" r="4" fill="#ea4335" />
      <circle cx="340" cy="280" r="4" fill="#ea4335" />
    </svg>
  );
};

export default DashboardScreenshot;
