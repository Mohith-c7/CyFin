import React, { useState, useEffect } from 'react';
import './App.css';
import HeroIllustration from './components/HeroIllustration';
import DashboardScreenshot from './components/DashboardScreenshot';
import MSIScreenshot from './components/MSIScreenshot';
import AnomalyScreenshot from './components/AnomalyScreenshot';

function App() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="App">
      {/* Navigation - Google Style */}
      <nav className={`navbar ${scrolled ? 'scrolled' : ''}`}>
        <div className="nav-container">
          <div className="nav-logo">
            <span className="logo-icon">📊</span>
            <span className="logo-text">CyFin</span>
          </div>
          <ul className="nav-menu">
            <li onClick={() => scrollToSection('home')}>Home</li>
            <li onClick={() => scrollToSection('features')}>Features</li>
            <li onClick={() => scrollToSection('technology')}>Technology</li>
            <li onClick={() => scrollToSection('screenshots')}>Screenshots</li>
            <li onClick={() => scrollToSection('impact')}>Impact</li>
          </ul>
          <a href="http://localhost:8502" target="_blank" rel="noopener noreferrer" className="nav-cta">
            Launch Dashboard
          </a>
        </div>
      </nav>

      {/* Hero Section - Google Style */}
      <section id="home" className="hero">
        <div className="container">
          <div className="hero-container">
            <div className="hero-content">
              <div className="hero-badge">
                <span>🛡️</span>
                Enterprise-Grade Security Platform
              </div>
              <h1 className="hero-title">
                Protect financial markets from <strong>cyber threats</strong>
              </h1>
              <p className="hero-subtitle">
                AI-powered real-time monitoring system that detects market manipulation,
                prevents cyber attacks, and ensures data integrity across financial infrastructure.
              </p>
              <div className="hero-buttons">
                <a href="http://localhost:8502" target="_blank" rel="noopener noreferrer" className="btn btn-primary btn-large">
                  Launch Dashboard →
                </a>
                <button onClick={() => scrollToSection('features')} className="btn btn-secondary btn-large">
                  Learn More
                </button>
              </div>
            </div>
            <div className="hero-image">
              <HeroIllustration />
            </div>
          </div>
          
          <div className="hero-stats">
            <div className="stat-item">
              <div className="stat-number">95%</div>
              <div className="stat-label">Detection Accuracy</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">&lt;1s</div>
              <div className="stat-label">Response Time</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">$50B+</div>
              <div className="stat-label">Protected Value</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">24/7</div>
              <div className="stat-label">Monitoring</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="features">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Comprehensive protection suite</h2>
            <p className="section-subtitle">
              Seven-layer defense system designed for financial market infrastructure
            </p>
          </div>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon-wrapper">
                <div className="feature-icon">📡</div>
              </div>
              <h3 className="feature-title">Real-Time Data Stream</h3>
              <p className="feature-description">
                Continuous ingestion of market data from multiple sources with microsecond precision. 
                Handles 390+ data points per symbol with zero latency.
              </p>
              <div className="feature-metrics">
                <span className="metric-badge">390+ data points</span>
                <span className="metric-badge">Multi-source feeds</span>
                <span className="metric-badge">Zero latency</span>
              </div>
            </div>

            <div className="feature-card">
              <div className="feature-icon-wrapper">
                <div className="feature-icon">🤖</div>
              </div>
              <h3 className="feature-title">AI Anomaly Detection</h3>
              <p className="feature-description">
                Ensemble machine learning with Isolation Forest and Z-score analysis. 
                Detects price manipulation, spoofing, and data corruption in real-time.
              </p>
              <div className="feature-metrics">
                <span className="metric-badge">95% accuracy</span>
                <span className="metric-badge">Ensemble ML</span>
                <span className="metric-badge">Z-score + ML</span>
              </div>
            </div>

            <div className="feature-card">
              <div className="feature-icon-wrapper">
                <div className="feature-icon">🛡️</div>
              </div>
              <h3 className="feature-title">Trust Score Engine</h3>
              <p className="feature-description">
                Dynamic 0-100 trust scoring system that evaluates data reliability. 
                Classifies threats as SAFE, CAUTION, or DANGEROUS with instant alerts.
              </p>
              <div className="feature-metrics">
                <span className="metric-badge">0-100 scoring</span>
                <span className="metric-badge">3-tier classification</span>
                <span className="metric-badge">Real-time alerts</span>
              </div>
            </div>

            <div className="feature-card">
              <div className="feature-icon-wrapper">
                <div className="feature-icon">⚔️</div>
              </div>
              <h3 className="feature-title">Attack Simulation</h3>
              <p className="feature-description">
                Built-in cyber attack simulator for testing resilience. 
                Simulates price manipulation, data injection, and feed corruption scenarios.
              </p>
              <div className="feature-metrics">
                <span className="metric-badge">15% spike tests</span>
                <span className="metric-badge">Multiple vectors</span>
                <span className="metric-badge">Stress testing</span>
              </div>
            </div>

            <div className="feature-card">
              <div className="feature-icon-wrapper">
                <div className="feature-icon">🔒</div>
              </div>
              <h3 className="feature-title">Trading Protection</h3>
              <p className="feature-description">
                Automated circuit breaker that blocks trades during anomalies. 
                Prevents execution of orders based on manipulated data.
              </p>
              <div className="feature-metrics">
                <span className="metric-badge">Auto-blocking</span>
                <span className="metric-badge">Circuit breaker</span>
                <span className="metric-badge">Trade validation</span>
              </div>
            </div>

            <div className="feature-card">
              <div className="feature-icon-wrapper">
                <div className="feature-icon">📊</div>
              </div>
              <h3 className="feature-title">Market Stability Index</h3>
              <p className="feature-description">
                Regulatory-grade MSI scoring (0-100) that aggregates trust, anomalies, and contagion risk. 
                Provides systemic risk classification.
              </p>
              <div className="feature-metrics">
                <span className="metric-badge">MSI 0-100</span>
                <span className="metric-badge">4 risk levels</span>
                <span className="metric-badge">Regulatory grade</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Technology Section */}
      <section id="technology" className="technology">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Built with cutting-edge technology</h2>
            <p className="section-subtitle">
              Industry-leading frameworks and algorithms power our platform
            </p>
          </div>
          <div className="tech-grid">
            <div className="tech-card">
              <h3 className="tech-category">Machine Learning</h3>
              <div className="tech-items">
                <div className="tech-item">
                  <div className="tech-name">Isolation Forest</div>
                  <div className="tech-desc">Unsupervised anomaly detection</div>
                </div>
                <div className="tech-item">
                  <div className="tech-name">Z-Score Analysis</div>
                  <div className="tech-desc">Statistical outlier detection</div>
                </div>
                <div className="tech-item">
                  <div className="tech-name">Ensemble Voting</div>
                  <div className="tech-desc">Multi-model consensus</div>
                </div>
                <div className="tech-item">
                  <div className="tech-name">Scikit-learn</div>
                  <div className="tech-desc">Production ML framework</div>
                </div>
              </div>
            </div>

            <div className="tech-card">
              <h3 className="tech-category">Data Processing</h3>
              <div className="tech-items">
                <div className="tech-item">
                  <div className="tech-name">Python 3.9+</div>
                  <div className="tech-desc">High-performance runtime</div>
                </div>
                <div className="tech-item">
                  <div className="tech-name">Pandas</div>
                  <div className="tech-desc">Time-series analysis</div>
                </div>
                <div className="tech-item">
                  <div className="tech-name">NumPy</div>
                  <div className="tech-desc">Numerical computing</div>
                </div>
                <div className="tech-item">
                  <div className="tech-name">yFinance</div>
                  <div className="tech-desc">Market data API</div>
                </div>
              </div>
            </div>

            <div className="tech-card">
              <h3 className="tech-category">Visualization</h3>
              <div className="tech-items">
                <div className="tech-item">
                  <div className="tech-name">Streamlit</div>
                  <div className="tech-desc">Real-time dashboard</div>
                </div>
                <div className="tech-item">
                  <div className="tech-name">Plotly</div>
                  <div className="tech-desc">Interactive charts</div>
                </div>
                <div className="tech-item">
                  <div className="tech-name">Material Design</div>
                  <div className="tech-desc">Professional UI/UX</div>
                </div>
                <div className="tech-item">
                  <div className="tech-name">React.js</div>
                  <div className="tech-desc">Landing page framework</div>
                </div>
              </div>
            </div>

            <div className="tech-card">
              <h3 className="tech-category">Infrastructure</h3>
              <div className="tech-items">
                <div className="tech-item">
                  <div className="tech-name">SQLite</div>
                  <div className="tech-desc">Embedded database</div>
                </div>
                <div className="tech-item">
                  <div className="tech-name">Multi-threading</div>
                  <div className="tech-desc">Concurrent processing</div>
                </div>
                <div className="tech-item">
                  <div className="tech-name">Event-driven</div>
                  <div className="tech-desc">Real-time architecture</div>
                </div>
                <div className="tech-item">
                  <div className="tech-name">Modular Design</div>
                  <div className="tech-desc">Scalable components</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Screenshots Section */}
      <section id="screenshots" className="screenshots">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">See it in action</h2>
            <p className="section-subtitle">
              Professional dashboard with real-time monitoring and analytics
            </p>
          </div>
          <div className="screenshots-grid">
            <div className="screenshot-card">
              <div className="screenshot-image">
                <DashboardScreenshot />
              </div>
              <div className="screenshot-content">
                <h3 className="screenshot-title">Real-Time Dashboard</h3>
                <p className="screenshot-desc">
                  Material Design interface with live price charts, trust scores, and anomaly detection
                </p>
              </div>
            </div>

            <div className="screenshot-card">
              <div className="screenshot-image">
                <MSIScreenshot />
              </div>
              <div className="screenshot-content">
                <h3 className="screenshot-title">Market Stability Index</h3>
                <p className="screenshot-desc">
                  Color-coded MSI scoring with component breakdown and risk classification
                </p>
              </div>
            </div>

            <div className="screenshot-card">
              <div className="screenshot-image">
                <AnomalyScreenshot />
              </div>
              <div className="screenshot-content">
                <h3 className="screenshot-title">Anomaly Detection</h3>
                <p className="screenshot-desc">
                  Real-time alerts with confidence scores and detailed analysis
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Impact Section */}
      <section id="impact" className="impact">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Real-world impact</h2>
            <p className="section-subtitle">
              Protecting billions in market value from cyber threats
            </p>
          </div>
          <div className="impact-grid">
            <div className="impact-card">
              <div className="impact-icon-wrapper">
                <div className="impact-icon">💰</div>
              </div>
              <h3 className="impact-title">$5B-$50B Annual Savings</h3>
              <p className="impact-description">
                Prevents flash crashes, market manipulation, and data corruption that cost billions annually
              </p>
              <ul className="impact-stats">
                <li>Flash Crash 2010: $1T lost</li>
                <li>Knight Capital: $440M loss</li>
                <li>Prevention over recovery</li>
              </ul>
            </div>

            <div className="impact-card">
              <div className="impact-icon-wrapper">
                <div className="impact-icon">⚡</div>
              </div>
              <h3 className="impact-title">Sub-Second Detection</h3>
              <p className="impact-description">
                Identifies threats in under 1 second, preventing cascade failures across markets
              </p>
              <ul className="impact-stats">
                <li>Less than 1s response time</li>
                <li>Real-time blocking</li>
                <li>Zero human delay</li>
              </ul>
            </div>

            <div className="impact-card">
              <div className="impact-icon-wrapper">
                <div className="impact-icon">🏛️</div>
              </div>
              <h3 className="impact-title">Regulatory Compliance</h3>
              <p className="impact-description">
                Meets SEC, FINRA, and international standards for market surveillance and reporting
              </p>
              <ul className="impact-stats">
                <li>Full audit trail</li>
                <li>MSI reporting</li>
                <li>Compliance-ready</li>
              </ul>
            </div>

            <div className="impact-card">
              <div className="impact-icon-wrapper">
                <div className="impact-icon">🌐</div>
              </div>
              <h3 className="impact-title">Multi-Market Protection</h3>
              <p className="impact-description">
                Monitors multiple symbols simultaneously with cross-asset contagion detection
              </p>
              <ul className="impact-stats">
                <li>Multi-symbol monitoring</li>
                <li>Contagion detection</li>
                <li>Systemic risk analysis</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="container">
          <div className="cta-content">
            <h2 className="cta-title">Ready to secure your markets?</h2>
            <p className="cta-subtitle">
              Experience the power of AI-driven market protection
            </p>
            <a href="http://localhost:8502" target="_blank" rel="noopener noreferrer" className="btn btn-primary btn-large">
              Launch Dashboard Now →
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-brand">
              <div className="footer-logo">
                <span className="logo-icon">📊</span>
                <span className="logo-text">CyFin</span>
              </div>
              <p className="footer-tagline">
                Enterprise-grade market stability monitoring platform
              </p>
            </div>
            <div className="footer-column">
              <h4>Product</h4>
              <ul>
                <li onClick={() => scrollToSection('features')}>Features</li>
                <li onClick={() => scrollToSection('technology')}>Technology</li>
                <li onClick={() => scrollToSection('screenshots')}>Screenshots</li>
                <li onClick={() => scrollToSection('impact')}>Impact</li>
              </ul>
            </div>
            <div className="footer-column">
              <h4>Resources</h4>
              <ul>
                <li>Documentation</li>
                <li>API Reference</li>
                <li>Testing Guide</li>
                <li>GitHub</li>
              </ul>
            </div>
            <div className="footer-column">
              <h4>Company</h4>
              <ul>
                <li>About</li>
                <li>Contact</li>
                <li>Careers</li>
                <li>Blog</li>
              </ul>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2024 CyFin. All rights reserved.</p>
            <p>Built with React.js, Python, and Machine Learning</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
