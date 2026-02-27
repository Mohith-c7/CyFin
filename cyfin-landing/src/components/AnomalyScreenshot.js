import React from 'react';

const AnomalyScreenshot = () => {
  return (
    <svg viewBox="0 0 600 400" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Background */}
      <rect width="600" height="400" fill="#fafafa" />
      
      {/* Browser chrome */}
      <rect x="0" y="0" width="600" height="40" fill="#f1f3f4" />
      <circle cx="20" cy="20" r="6" fill="#ea4335" />
      <circle cx="40" cy="20" r="6" fill="#fbbc04" />
      <circle cx="60" cy="20" r="6" fill="#34a853" />
      
      {/* Alert card */}
      <rect x="40" y="70" width="520" height="120" rx="8" fill="#fce8e6" stroke="#ea4335" strokeWidth="2" />
      <text x="70" y="100" fontSize="24">🚨</text>
      <text x="110" y="105" fill="#ea4335" fontSize="18" fontWeight="bold">CYBER ATTACK DETECTED</text>
      <text x="70" y="135" fill="#5f6368" fontSize="14">Price manipulation at step 45: $182.50 → $210.88 (+15.5%)</text>
      <text x="70" y="160" fill="#5f6368" fontSize="12">Confidence: 95% | Z-Score: 4.2 | Trust: DANGEROUS</text>
      
      {/* Detection details */}
      <rect x="40" y="210" width="520" height="140" rx="8" fill="white" stroke="#dadce0" strokeWidth="1" />
      
      <text x="60" y="240" fill="#202124" fontSize="16" fontWeight="bold">Anomaly Detection Details</text>
      
      {/* Detection methods */}
      <rect x="60" y="260" width="240" height="70" rx="6" fill="#e8f0fe" />
      <text x="80" y="285" fill="#5f6368" fontSize="12" fontWeight="500">Z-Score Analysis</text>
      <text x="80" y="305" fill="#1a73e8" fontSize="20" fontWeight="bold">4.2σ</text>
      <text x="80" y="320" fill="#ea4335" fontSize="11">ANOMALY</text>
      
      <rect x="320" y="260" width="240" height="70" rx="6" fill="#e8f5e9" />
      <text x="340" y="285" fill="#5f6368" fontSize="12" fontWeight="500">Isolation Forest</text>
      <text x="340" y="305" fill="#34a853" fontSize="20" fontWeight="bold">95%</text>
      <text x="340" y="320" fill="#ea4335" fontSize="11">ANOMALY</text>
      
      {/* Timeline indicator */}
      <line x1="60" y1="365" x2="540" y2="365" stroke="#dadce0" strokeWidth="2" />
      <circle cx="200" cy="365" r="8" fill="#34a853" />
      <circle cx="350" cy="365" r="8" fill="#ea4335" />
      <circle cx="450" cy="365" r="8" fill="#ea4335" />
      <text x="185" y="385" fill="#5f6368" fontSize="10">Normal</text>
      <text x="330" y="385" fill="#ea4335" fontSize="10">Attack 1</text>
      <text x="430" y="385" fill="#ea4335" fontSize="10">Attack 2</text>
    </svg>
  );
};

export default AnomalyScreenshot;
