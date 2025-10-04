/**
 * Google Analytics 4 Integration
 *
 * This module provides a wrapper around Google Analytics 4 (GA4) that:
 * - Respects user cookie consent preferences
 * - Only initializes when analytics consent is granted
 * - Provides helper functions for common tracking events
 */

// Check if user has consented to analytics
export const hasAnalyticsConsent = () => {
  try {
    const consent = localStorage.getItem('cookieConsent');
    if (!consent) return false;

    const preferences = JSON.parse(consent);
    return preferences.analytics === true;
  } catch (e) {
    console.error('Error checking analytics consent:', e);
    return false;
  }
};

// Initialize Google Analytics 4
export const initGA = () => {
  // Only initialize if user has consented
  if (!hasAnalyticsConsent()) {
    console.log('📊 GA4: Analytics consent not granted, skipping initialization');
    return;
  }

  const measurementId = process.env.REACT_APP_GA_MEASUREMENT_ID;

  if (!measurementId) {
    console.warn('📊 GA4: Measurement ID not configured');
    return;
  }

  // Check if gtag is already loaded
  if (window.gtag) {
    console.log('📊 GA4: Already initialized');
    return;
  }

  // Load gtag.js script
  const script = document.createElement('script');
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${measurementId}`;
  document.head.appendChild(script);

  // Initialize gtag
  window.dataLayer = window.dataLayer || [];
  window.gtag = function() {
    window.dataLayer.push(arguments);
  };
  window.gtag('js', new Date());
  window.gtag('config', measurementId, {
    send_page_view: true,
    cookie_flags: 'SameSite=None;Secure', // For HTTPS sites
  });

  console.log('✅ GA4: Initialized with measurement ID:', measurementId);
};

// Remove GA4 scripts and data (when user revokes consent)
export const removeGA = () => {
  // Remove gtag function
  if (window.gtag) {
    delete window.gtag;
  }

  // Clear dataLayer
  if (window.dataLayer) {
    window.dataLayer = [];
  }

  // Remove gtag script tags
  const scripts = document.querySelectorAll('script[src*="googletagmanager.com/gtag"]');
  scripts.forEach(script => script.remove());

  // Clear GA cookies
  const gaCookies = document.cookie.split(';').filter(cookie =>
    cookie.trim().startsWith('_ga') ||
    cookie.trim().startsWith('_gid') ||
    cookie.trim().startsWith('_gat')
  );

  gaCookies.forEach(cookie => {
    const cookieName = cookie.split('=')[0].trim();
    document.cookie = `${cookieName}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
  });

  console.log('🗑️ GA4: Removed scripts and cookies');
};

// Track page view
export const trackPageView = (pagePath, pageTitle) => {
  if (!hasAnalyticsConsent() || !window.gtag) {
    return;
  }

  window.gtag('event', 'page_view', {
    page_path: pagePath,
    page_title: pageTitle,
  });

  console.log('📊 GA4: Page view tracked:', pagePath);
};

// Track custom event
export const trackEvent = (eventName, eventParams = {}) => {
  if (!hasAnalyticsConsent() || !window.gtag) {
    return;
  }

  window.gtag('event', eventName, eventParams);
  console.log('📊 GA4: Event tracked:', eventName, eventParams);
};

// Predefined event trackers for common actions
export const analytics = {
  // User authentication events
  trackLogin: (method) => {
    trackEvent('login', { method }); // method: 'email', 'google'
  },

  trackSignup: (method) => {
    trackEvent('sign_up', { method });
  },

  trackLogout: () => {
    trackEvent('logout');
  },

  // Tournament events
  trackTournamentCreated: (tournamentId, system) => {
    trackEvent('tournament_created', {
      tournament_id: tournamentId,
      tournament_system: system,
    });
  },

  trackTournamentJoined: (tournamentId) => {
    trackEvent('tournament_joined', {
      tournament_id: tournamentId,
    });
  },

  trackTournamentStarted: (tournamentId) => {
    trackEvent('tournament_started', {
      tournament_id: tournamentId,
    });
  },

  trackTournamentCompleted: (tournamentId) => {
    trackEvent('tournament_completed', {
      tournament_id: tournamentId,
    });
  },

  trackMatchResultRecorded: (matchId, tournamentId) => {
    trackEvent('match_result_recorded', {
      match_id: matchId,
      tournament_id: tournamentId,
    });
  },

  // Navigation events
  trackNavigation: (destination) => {
    trackEvent('navigation', {
      destination,
    });
  },

  // Search events
  trackSearch: (searchTerm, resultCount) => {
    trackEvent('search', {
      search_term: searchTerm,
      result_count: resultCount,
    });
  },

  // Cookie consent events
  trackConsentGiven: (analytics, marketing) => {
    trackEvent('cookie_consent_given', {
      analytics_consent: analytics,
      marketing_consent: marketing,
    });
  },

  trackConsentRevoked: () => {
    trackEvent('cookie_consent_revoked');
  },
};

export default analytics;
