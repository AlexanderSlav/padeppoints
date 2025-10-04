import React, { useState, useEffect } from 'react';
import './CookieConsent.css';
import { initGA, removeGA, analytics } from '../utils/analytics';

const CookieConsent = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [showPreferences, setShowPreferences] = useState(false);
  const [preferences, setPreferences] = useState({
    necessary: true, // Always true, cannot be disabled
    analytics: false,
    marketing: false,
  });

  useEffect(() => {
    // Check if user has already made a choice
    const consent = localStorage.getItem('cookieConsent');
    if (!consent) {
      // Show banner after a small delay for better UX
      setTimeout(() => setIsVisible(true), 500);
    } else {
      // Load saved preferences
      try {
        const savedPreferences = JSON.parse(consent);
        setPreferences(savedPreferences);
      } catch (e) {
        console.error('Error parsing cookie consent:', e);
      }
    }
  }, []);

  const handleAcceptAll = () => {
    const allAccepted = {
      necessary: true,
      analytics: true,
      marketing: true,
    };
    saveConsent(allAccepted);
  };

  const handleRejectAll = () => {
    const onlyNecessary = {
      necessary: true,
      analytics: false,
      marketing: false,
    };
    saveConsent(onlyNecessary);
  };

  const handleSavePreferences = () => {
    saveConsent(preferences);
  };

  const saveConsent = (consentPreferences) => {
    localStorage.setItem('cookieConsent', JSON.stringify(consentPreferences));
    setPreferences(consentPreferences);
    setIsVisible(false);
    setShowPreferences(false);

    // Initialize or remove analytics based on consent
    if (consentPreferences.analytics) {
      initGA();
      analytics.trackConsentGiven(true, consentPreferences.marketing);
    } else {
      removeGA();
      analytics.trackConsentRevoked();
    }

    // Initialize marketing cookies if consented
    if (consentPreferences.marketing) {
      // Future: Initialize marketing scripts (Facebook Pixel, etc.)
      console.log('Marketing cookies enabled');
    }
  };

  const handlePreferenceChange = (category) => {
    if (category === 'necessary') return; // Cannot disable necessary cookies
    setPreferences({
      ...preferences,
      [category]: !preferences[category],
    });
  };

  if (!isVisible) return null;

  return (
    <div className="cookie-consent-overlay">
      <div className="cookie-consent-container">
        {!showPreferences ? (
          // Main consent view
          <div className="cookie-consent-content">
            <div className="cookie-consent-header">
              <span className="cookie-icon">🍪</span>
              <h3>We value your privacy</h3>
            </div>

            <p className="cookie-consent-text">
              We use cookies to enhance your browsing experience, analyze site traffic, and personalize content.
              By clicking "Accept All", you consent to our use of cookies. You can customize your preferences or
              reject non-essential cookies.
            </p>

            <a href="/privacy-policy" className="cookie-policy-link" target="_blank" rel="noopener noreferrer">
              Read our Cookie Policy
            </a>

            <div className="cookie-consent-actions">
              <button
                className="btn-cookie btn-cookie-secondary"
                onClick={handleRejectAll}
                aria-label="Reject all non-essential cookies"
              >
                Reject All
              </button>
              <button
                className="btn-cookie btn-cookie-ghost"
                onClick={() => setShowPreferences(true)}
                aria-label="Customize cookie preferences"
              >
                Customize
              </button>
              <button
                className="btn-cookie btn-cookie-primary"
                onClick={handleAcceptAll}
                aria-label="Accept all cookies"
              >
                Accept All
              </button>
            </div>
          </div>
        ) : (
          // Preferences view
          <div className="cookie-consent-content">
            <div className="cookie-consent-header">
              <button
                className="cookie-back-button"
                onClick={() => setShowPreferences(false)}
                aria-label="Go back to main cookie consent"
              >
                ← Back
              </button>
              <h3>Cookie Preferences</h3>
            </div>

            <div className="cookie-preferences">
              <div className="cookie-category">
                <div className="cookie-category-header">
                  <div>
                    <h4>Necessary Cookies</h4>
                    <p className="cookie-category-description">
                      Essential for the website to function properly. These cannot be disabled.
                    </p>
                  </div>
                  <label className="cookie-toggle">
                    <input
                      type="checkbox"
                      checked={preferences.necessary}
                      disabled
                      aria-label="Necessary cookies - always enabled"
                    />
                    <span className="cookie-toggle-slider disabled"></span>
                  </label>
                </div>
              </div>

              <div className="cookie-category">
                <div className="cookie-category-header">
                  <div>
                    <h4>Analytics Cookies</h4>
                    <p className="cookie-category-description">
                      Help us understand how visitors interact with our website to improve user experience.
                    </p>
                  </div>
                  <label className="cookie-toggle">
                    <input
                      type="checkbox"
                      checked={preferences.analytics}
                      onChange={() => handlePreferenceChange('analytics')}
                      aria-label="Toggle analytics cookies"
                    />
                    <span className="cookie-toggle-slider"></span>
                  </label>
                </div>
              </div>

              <div className="cookie-category">
                <div className="cookie-category-header">
                  <div>
                    <h4>Marketing Cookies</h4>
                    <p className="cookie-category-description">
                      Used to deliver personalized advertisements and track ad campaign performance.
                    </p>
                  </div>
                  <label className="cookie-toggle">
                    <input
                      type="checkbox"
                      checked={preferences.marketing}
                      onChange={() => handlePreferenceChange('marketing')}
                      aria-label="Toggle marketing cookies"
                    />
                    <span className="cookie-toggle-slider"></span>
                  </label>
                </div>
              </div>
            </div>

            <div className="cookie-consent-actions">
              <button
                className="btn-cookie btn-cookie-secondary"
                onClick={() => setShowPreferences(false)}
                aria-label="Cancel and go back"
              >
                Cancel
              </button>
              <button
                className="btn-cookie btn-cookie-primary"
                onClick={handleSavePreferences}
                aria-label="Save cookie preferences"
              >
                Save Preferences
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CookieConsent;
