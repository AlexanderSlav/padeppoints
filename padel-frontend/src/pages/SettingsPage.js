import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../components/AuthContext';

const SettingsPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');

  if (!user) {
    navigate('/login');
    return null;
  }

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      {/* Header */}
      <div style={{
        backgroundColor: 'white',
        borderRadius: '16px',
        padding: '24px',
        marginBottom: '24px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
      }}>
        <button
          onClick={() => navigate(-1)}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 16px',
            backgroundColor: 'transparent',
            border: '1px solid #e2e8f0',
            borderRadius: '8px',
            color: '#4a5568',
            fontSize: '14px',
            fontWeight: '500',
            cursor: 'pointer',
            marginBottom: '20px',
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => {
            e.target.style.backgroundColor = '#f7fafc';
            e.target.style.borderColor = '#cbd5e0';
          }}
          onMouseLeave={(e) => {
            e.target.style.backgroundColor = 'transparent';
            e.target.style.borderColor = '#e2e8f0';
          }}
        >
          ← Back
        </button>

        <h1 style={{
          margin: '0 0 8px 0',
          fontSize: '32px',
          fontWeight: 'bold',
          color: '#1a202c'
        }}>
          Settings
        </h1>
        <p style={{
          margin: 0,
          color: '#718096',
          fontSize: '14px'
        }}>
          Manage your account settings and preferences
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '250px 1fr', gap: '24px' }}>
        {/* Sidebar Navigation */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '16px',
          padding: '16px',
          height: 'fit-content',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
        }}>
          <nav>
            <button
              onClick={() => setActiveTab('profile')}
              style={{
                width: '100%',
                padding: '12px 16px',
                backgroundColor: activeTab === 'profile' ? '#f0f4f8' : 'transparent',
                border: 'none',
                borderRadius: '8px',
                textAlign: 'left',
                fontSize: '14px',
                fontWeight: activeTab === 'profile' ? '600' : '500',
                color: activeTab === 'profile' ? '#4299e1' : '#4a5568',
                cursor: 'pointer',
                marginBottom: '4px',
                transition: 'all 0.2s'
              }}
            >
              Profile
            </button>
            <button
              onClick={() => setActiveTab('subscription')}
              style={{
                width: '100%',
                padding: '12px 16px',
                backgroundColor: activeTab === 'subscription' ? '#f0f4f8' : 'transparent',
                border: 'none',
                borderRadius: '8px',
                textAlign: 'left',
                fontSize: '14px',
                fontWeight: activeTab === 'subscription' ? '600' : '500',
                color: activeTab === 'subscription' ? '#4299e1' : '#4a5568',
                cursor: 'pointer',
                marginBottom: '4px',
                transition: 'all 0.2s'
              }}
            >
              Subscription
            </button>
            <button
              onClick={() => setActiveTab('account')}
              style={{
                width: '100%',
                padding: '12px 16px',
                backgroundColor: activeTab === 'account' ? '#f0f4f8' : 'transparent',
                border: 'none',
                borderRadius: '8px',
                textAlign: 'left',
                fontSize: '14px',
                fontWeight: activeTab === 'account' ? '600' : '500',
                color: activeTab === 'account' ? '#4299e1' : '#4a5568',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              Account
            </button>
          </nav>
        </div>

        {/* Content Area */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '16px',
          padding: '32px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
        }}>
          {activeTab === 'profile' && (
            <div>
              <h2 style={{
                margin: '0 0 24px 0',
                fontSize: '20px',
                fontWeight: '600',
                color: '#1a202c'
              }}>
                Profile Settings
              </h2>

              {/* Profile Picture */}
              <div style={{ marginBottom: '32px' }}>
                <label style={{
                  display: 'block',
                  fontSize: '14px',
                  fontWeight: '500',
                  color: '#4a5568',
                  marginBottom: '8px'
                }}>
                  Profile Picture
                </label>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <div style={{
                    width: '80px',
                    height: '80px',
                    borderRadius: '50%',
                    backgroundColor: '#e2e8f0',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '32px',
                    fontWeight: '600',
                    color: '#718096'
                  }}>
                    {user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
                  </div>
                  <div>
                    <button style={{
                      padding: '8px 16px',
                      backgroundColor: 'white',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '14px',
                      fontWeight: '500',
                      color: '#4a5568',
                      cursor: 'pointer',
                      marginRight: '8px'
                    }}>
                      Upload Photo
                    </button>
                    <button style={{
                      padding: '8px 16px',
                      backgroundColor: 'white',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '14px',
                      fontWeight: '500',
                      color: '#ef4444',
                      cursor: 'pointer'
                    }}>
                      Remove
                    </button>
                  </div>
                </div>
              </div>

              {/* Name Field */}
              <div style={{ marginBottom: '24px' }}>
                <label style={{
                  display: 'block',
                  fontSize: '14px',
                  fontWeight: '500',
                  color: '#4a5568',
                  marginBottom: '8px'
                }}>
                  Full Name
                </label>
                <input
                  type="text"
                  defaultValue={user?.full_name || ''}
                  style={{
                    width: '100%',
                    maxWidth: '400px',
                    padding: '10px 12px',
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    fontSize: '14px',
                    color: '#1a202c'
                  }}
                />
              </div>

              {/* Email Field */}
              <div style={{ marginBottom: '24px' }}>
                <label style={{
                  display: 'block',
                  fontSize: '14px',
                  fontWeight: '500',
                  color: '#4a5568',
                  marginBottom: '8px'
                }}>
                  Email
                </label>
                <input
                  type="email"
                  defaultValue={user?.email || ''}
                  disabled
                  style={{
                    width: '100%',
                    maxWidth: '400px',
                    padding: '10px 12px',
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    fontSize: '14px',
                    color: '#718096',
                    backgroundColor: '#f7fafc',
                    cursor: 'not-allowed'
                  }}
                />
                <p style={{
                  margin: '4px 0 0 0',
                  fontSize: '12px',
                  color: '#718096'
                }}>
                  Email cannot be changed
                </p>
              </div>

              {/* Profile Status */}
              <div style={{ marginBottom: '32px' }}>
                <label style={{
                  display: 'block',
                  fontSize: '14px',
                  fontWeight: '500',
                  color: '#4a5568',
                  marginBottom: '8px'
                }}>
                  Profile Status
                </label>
                <select
                  style={{
                    width: '100%',
                    maxWidth: '400px',
                    padding: '10px 12px',
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    fontSize: '14px',
                    color: '#1a202c',
                    backgroundColor: 'white',
                    cursor: 'pointer'
                  }}
                >
                  <option value="active">Active - Visible in searches</option>
                  <option value="inactive">Inactive - Hidden from searches</option>
                </select>
              </div>

              {/* Save Button */}
              <button
                style={{
                  padding: '12px 24px',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'transform 0.2s, box-shadow 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.3)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = 'none';
                }}
              >
                Save Changes
              </button>
            </div>
          )}

          {activeTab === 'subscription' && (
            <div>
              <h2 style={{
                margin: '0 0 24px 0',
                fontSize: '20px',
                fontWeight: '600',
                color: '#1a202c'
              }}>
                Subscription Management
              </h2>

              <div style={{
                padding: '24px',
                backgroundColor: '#f7fafc',
                borderRadius: '12px',
                border: '1px solid #e2e8f0',
                marginBottom: '24px'
              }}>
                <h3 style={{
                  margin: '0 0 8px 0',
                  fontSize: '16px',
                  fontWeight: '600',
                  color: '#1a202c'
                }}>
                  Free Plan
                </h3>
                <p style={{
                  margin: '0 0 16px 0',
                  fontSize: '14px',
                  color: '#4a5568'
                }}>
                  You are currently on the free plan
                </p>
                <div style={{
                  fontSize: '13px',
                  color: '#718096'
                }}>
                  <div style={{ marginBottom: '4px' }}>✓ Join tournaments</div>
                  <div style={{ marginBottom: '4px' }}>✓ Track your statistics</div>
                  <div style={{ marginBottom: '4px' }}>✓ View leaderboards</div>
                </div>
              </div>

              <div style={{
                padding: '20px',
                backgroundColor: '#f0f4f8',
                borderRadius: '12px',
                textAlign: 'center'
              }}>
                <p style={{
                  margin: '0',
                  fontSize: '14px',
                  color: '#718096'
                }}>
                  Premium plans coming soon!
                </p>
              </div>
            </div>
          )}

          {activeTab === 'account' && (
            <div>
              <h2 style={{
                margin: '0 0 24px 0',
                fontSize: '20px',
                fontWeight: '600',
                color: '#1a202c'
              }}>
                Account Settings
              </h2>

              {/* Privacy Settings */}
              <div style={{ marginBottom: '32px' }}>
                <h3 style={{
                  margin: '0 0 16px 0',
                  fontSize: '16px',
                  fontWeight: '600',
                  color: '#1a202c'
                }}>
                  Privacy
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  <label style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    fontSize: '14px',
                    color: '#4a5568',
                    cursor: 'pointer'
                  }}>
                    <input type="checkbox" defaultChecked />
                    Show my profile in public leaderboards
                  </label>
                  <label style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    fontSize: '14px',
                    color: '#4a5568',
                    cursor: 'pointer'
                  }}>
                    <input type="checkbox" defaultChecked />
                    Allow other players to view my tournament history
                  </label>
                </div>
              </div>

              {/* Danger Zone */}
              <div style={{
                padding: '20px',
                border: '1px solid #fee2e2',
                borderRadius: '12px',
                backgroundColor: '#fef2f2'
              }}>
                <h3 style={{
                  margin: '0 0 8px 0',
                  fontSize: '16px',
                  fontWeight: '600',
                  color: '#991b1b'
                }}>
                  Danger Zone
                </h3>
                <p style={{
                  margin: '0 0 16px 0',
                  fontSize: '14px',
                  color: '#7f1d1d'
                }}>
                  Once you delete your account, there is no going back. Please be certain.
                </p>
                <button
                  style={{
                    padding: '10px 20px',
                    backgroundColor: '#ef4444',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontWeight: '500',
                    cursor: 'pointer'
                  }}
                >
                  Delete Account
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;