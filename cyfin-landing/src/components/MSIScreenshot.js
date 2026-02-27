import React from 'react';

const MSIScreenshot = () => {
  return (
    <svg viewBox="0 0 600 400" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Background */}
      <rect width="600" height="400" fill="#fafafa" />
      
      {/* Browser chrome */}
      <rect x="0" y="0" width="600" height="40" fill="#f1f3f4" />
      <circle cx="20" cy="20" r="6" fill="#ea4335" />
      <circle cx="40" cy="20" r="6" fill="#fbbc04" />
      <circle cx="60" cy="20" r="6" fill="#34a853" />
      
      {/* MSI Card */}
      <rect x="40" y="70" width="520" height="280" rx="12" fill="white" stroke="#34a853" strokeWidth="3" />
      
      {/* Header */}
      <text x="60" y="105" fill="#5f6368" fontSize="12" fontWeight="500">MARKET STABILITY INDEX</text>
      
      {/* Large MSI number */}
      <text x="60" y="200" fill="#34a853" fontSize="96" fontWeight="300">87</text>
      
      {/* Status */}
      <rect x="350" y="140" width="180" height="80" rx="8" fill="#e8f5e9" />
      <text x="370" y="170" fill="#34a853" fontSize="24" fontWeight="bold">STABLE</text>
      <text x="370" y="200" fill="#5f6368" fontSize="14">Risk Level: LOW</text>
      
      {/* Component breakdown */}
      <rect x="60" y="230" width="500" height="100" rx="8" fill="#f8f9fa" />
      
      <text x="80" y="255" fill="#5f6368" fontSize="12">Trust Contribution</text>
      <text x="450" y="255" fill="#34a853" fontSize="12" fontWeight="bold">+55.00</text>
      
      <text x="80" y="280" fill="#5f6368" fontSize="12">Anomaly Rate Penalty</text>
      <text x="450" y="280" fill="#ea4335" fontSize="12" fontWeight="bold">-2.40</text>
      
      <text x="80" y="305" fill="#5f6368" fontSize="12">Feed Mismatch Penalty</text>
      <text x="450" y="305" fill="#ea4335" fontSize="12" fontWeight="bold">-0.50</text>
      
      {/* Status badge */}
      <rect x="350" y="250" width="80" height="28" rx="14" fill="#34a853" />
      <text x="365" y="270" fill="white" fontSize="12" fontWeight="bold">STABLE</text>
    </svg>
  );
};

export default MSIScreenshot;
