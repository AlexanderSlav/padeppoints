import React from 'react';
import { useNavigate } from 'react-router-dom';
import './LandingPage.css';

const LandingPage = () => {
  const navigate = useNavigate();

  const handleGetStarted = () => {
    navigate('/register');
  };

  const handleLogin = () => {
    navigate('/login');
  };

  return (
    <div className="landing-page">
      <nav className="landing-nav">
        <div className="nav-container">
          <div className="logo">
            <span className="logo-icon">🎾</span>
            <span className="logo-text">PadelPoints</span>
          </div>
          <div className="nav-links">
            <button className="nav-link" onClick={handleLogin}>Sign In</button>
            <button className="nav-cta" onClick={handleGetStarted}>Get Started</button>
          </div>
        </div>
      </nav>

      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">
            Organize Perfect <span className="highlight">Padel Tournaments</span>
          </h1>
          <p className="hero-subtitle">
            Streamline your padel tournaments with automatic match scheduling, 
            real-time scoring, and comprehensive player statistics
          </p>
          <div className="hero-actions">
            <button className="btn-primary" onClick={handleGetStarted}>
              Try PadelPoints Free
            </button>
            <button className="btn-secondary" onClick={() => document.getElementById('features').scrollIntoView({ behavior: 'smooth' })}>
              Learn More
            </button>
          </div>
          <div className="hero-stats">
            <div className="stat">
              <span className="stat-number">1000+</span>
              <span className="stat-label">Active Players</span>
            </div>
            <div className="stat">
              <span className="stat-number">500+</span>
              <span className="stat-label">Tournaments</span>
            </div>
            <div className="stat">
              <span className="stat-number">10k+</span>
              <span className="stat-label">Matches Played</span>
            </div>
          </div>
        </div>
        <div className="hero-visual">
          <div className="floating-card card-1">
            <div className="card-icon">🏆</div>
            <div className="card-text">Tournament Created</div>
          </div>
          <div className="floating-card card-2">
            <div className="card-icon">👥</div>
            <div className="card-text">8 Players Joined</div>
          </div>
          <div className="floating-card card-3">
            <div className="card-icon">📊</div>
            <div className="card-text">Live Leaderboard</div>
          </div>
        </div>
      </section>

      <section id="features" className="features">
        <div className="features-container">
          <div className="features-header">
            <h2>Everything You Need for Perfect Tournaments</h2>
            <p>Powerful features designed for padel enthusiasts and organizers</p>
          </div>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🎮</div>
              <h3>Multiple Tournament Formats</h3>
              <p>Support for Americano, Mexicano, and more tournament systems with automatic pairing algorithms</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h3>Real-time Scoring</h3>
              <p>Update scores instantly and watch the leaderboard change in real-time as matches progress</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📈</div>
              <h3>Player Statistics</h3>
              <p>Track performance metrics, win rates, and rankings across all tournaments</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🤝</div>
              <h3>Smart Matchmaking</h3>
              <p>Intelligent pairing system ensures balanced matches and maximum court utilization</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📱</div>
              <h3>Mobile Friendly</h3>
              <p>Access and manage tournaments from any device, anywhere, anytime</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🏅</div>
              <h3>ELO Rating System</h3>
              <p>Professional rating system to track player skill levels and ensure competitive balance</p>
            </div>
          </div>
        </div>
      </section>

      <section className="how-it-works">
        <div className="how-container">
          <h2>How It Works</h2>
          <p className="how-subtitle">Get your tournament running in minutes</p>
          <div className="steps">
            <div className="step">
              <div className="step-number">1</div>
              <h3>Create Tournament</h3>
              <p>Set up your tournament with custom rules, format, and scoring system</p>
            </div>
            <div className="step-arrow">→</div>
            <div className="step">
              <div className="step-number">2</div>
              <h3>Invite Players</h3>
              <p>Share the tournament link and let players join with a single click</p>
            </div>
            <div className="step-arrow">→</div>
            <div className="step">
              <div className="step-number">3</div>
              <h3>Play & Score</h3>
              <p>Generate rounds automatically and update scores as matches complete</p>
            </div>
          </div>
        </div>
      </section>

      <section className="testimonials">
        <div className="testimonials-container">
          <h2>Loved by Padel Communities</h2>
          <div className="testimonials-grid">
            <div className="testimonial">
              <div className="stars">⭐⭐⭐⭐⭐</div>
              <p>"PadelPoints transformed how we run our weekly tournaments. The automatic pairing saves us hours!"</p>
              <div className="testimonial-author">
                <strong>Carlos M.</strong>
                <span>Tournament Organizer</span>
              </div>
            </div>
            <div className="testimonial">
              <div className="stars">⭐⭐⭐⭐⭐</div>
              <p>"Finally, a tournament system that handles Americano format properly. The scoring is perfect!"</p>
              <div className="testimonial-author">
                <strong>Sofia L.</strong>
                <span>Padel Club Manager</span>
              </div>
            </div>
            <div className="testimonial">
              <div className="stars">⭐⭐⭐⭐⭐</div>
              <p>"Love the ELO rating system! It helps us create balanced matches every time."</p>
              <div className="testimonial-author">
                <strong>Miguel R.</strong>
                <span>Pro Player</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="cta">
        <div className="cta-container">
          <h2>Ready to Elevate Your Padel Tournaments?</h2>
          <p>Join thousands of players and organizers using PadelPoints</p>
          <button className="cta-button" onClick={handleGetStarted}>
            Start Free Today
          </button>
        </div>
      </section>

      <footer className="landing-footer">
        <div className="footer-container">
          <div className="footer-brand">
            <div className="logo">
              <span className="logo-icon">🎾</span>
              <span className="logo-text">PadelPoints</span>
            </div>
            <p>Making padel tournaments simple and fun</p>
          </div>
          <div className="footer-links">
            <div className="footer-column">
              <h4>Product</h4>
              <a href="#features">Features</a>
              <a href="#how-it-works">How it Works</a>
              <a href="/login">Sign In</a>
            </div>
            <div className="footer-column">
              <h4>Company</h4>
              <a href="#">About</a>
              <a href="#">Contact</a>
              <a href="#">Privacy</a>
            </div>
          </div>
        </div>
        <div className="footer-bottom">
          <p>© 2024 PadelPoints. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;