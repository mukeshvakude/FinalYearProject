/**
 * Professional Login Component
 * 
 * A clean, responsive login form with validation and error handling.
 * Supports username/password authentication with encryption password.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { authService } from '../services/apiService';
import '../css/Professional.css';
import './Components.css';

function Login() {
  // Form State
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [encryptionPassword, setEncryptionPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showEpass, setShowEpass] = useState(false);

  // UI State
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [validationErrors, setValidationErrors] = useState({});

  // Navigation
  const navigate = useNavigate();
  const location = useLocation();

  // Check if user is already authenticated
  useEffect(() => {
    const checkAuthentication = async () => {
      try {
        await authService.getSession();
        navigate('/home');
      } catch (err) {
        // User not authenticated, stay on login
      }
    };

    checkAuthentication();
  }, [navigate]);

  /**
   * Validate form inputs
   * @returns {Object} Validation errors object
   */
  const validateForm = () => {
    const errors = {};

    if (!username.trim()) {
      errors.username = 'Username is required';
    } else if (username.trim().length < 3) {
      errors.username = 'Username must be at least 3 characters';
    }

    if (!password.trim()) {
      errors.password = 'Password is required';
    } else if (password.trim().length < 3) {
      errors.password = 'Password must be at least 3 characters';
    }

    if (!encryptionPassword.trim()) {
      errors.encryptionPassword = 'Encryption password is required';
    } else if (encryptionPassword.trim().length < 3) {
      errors.encryptionPassword = 'Encryption password must be at least 3 characters';
    }

    return errors;
  };

  /**
   * Handle form submission
   */
  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate form
    const errors = validateForm();
    if (Object.keys(errors).length > 0) {
      setValidationErrors(errors);
      setError('Please fix the errors below');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');
    setValidationErrors({});

    try {
      const result = await authService.login(
        username.trim(),
        password.trim(),
        encryptionPassword.trim()
      );

      if (result.success) {
        setSuccess('Login successful! Redirecting...');
        setTimeout(() => {
          navigate('/home');
        }, 1000);
      } else {
        setError(result.error || 'Login failed');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'An error occurred during login';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle demo login
   */
  const handleDemoLogin = async (e) => {
    e.preventDefault();
    setUsername('admin');
    setPassword('admin');
    setEncryptionPassword('admin');
    setValidationErrors({});
  };

  return (
    <div className="login-container">
      <div className="login-wrapper">
        <div className="w3-card-4 login-card">
          {/* Header */}
          <header className="w3-container login-header">
            <h1>🔐 Steganography</h1>
            <p className="login-subtitle">Secure Message Hiding & Encryption</p>
          </header>

          {/* Alert Messages */}
          {error && (
            <div className="alert-container">
              <div className="alert alert-error">
                <strong>Error:</strong> {error}
              </div>
            </div>
          )}

          {success && (
            <div className="alert-container">
              <div className="alert alert-success">
                <strong>Success:</strong> {success}
              </div>
            </div>
          )}

          {/* Login Form */}
          <form className="w3-container login-form" onSubmit={handleSubmit}>
            {/* Username Field */}
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                id="username"
                type="text"
                className={`w3-input ${validationErrors.username ? 'input-error' : ''}`}
                value={username}
                onChange={(e) => {
                  setUsername(e.target.value);
                  setValidationErrors({ ...validationErrors, username: '' });
                }}
                placeholder="Enter your username"
                disabled={loading}
                autoComplete="username"
              />
              {validationErrors.username && (
                <span className="error-message">{validationErrors.username}</span>
              )}
            </div>

            {/* Password Field */}
            <div className="form-group">
              <label htmlFor="password">Login Password</label>
              <div className="password-input-wrapper">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  className={`w3-input ${validationErrors.password ? 'input-error' : ''}`}
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    setValidationErrors({ ...validationErrors, password: '' });
                  }}
                  placeholder="Enter your password"
                  disabled={loading}
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  className="toggle-password"
                  onClick={() => setShowPassword(!showPassword)}
                  title={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? '👁️' : '👁️‍🗨️'}
                </button>
              </div>
              {validationErrors.password && (
                <span className="error-message">{validationErrors.password}</span>
              )}
            </div>

            {/* Encryption Password Field */}
            <div className="form-group">
              <label htmlFor="encryptionPassword">Encryption Password</label>
              <div className="password-input-wrapper">
                <input
                  id="encryptionPassword"
                  type={showEpass ? 'text' : 'password'}
                  className={`w3-input ${validationErrors.encryptionPassword ? 'input-error' : ''}`}
                  value={encryptionPassword}
                  onChange={(e) => {
                    setEncryptionPassword(e.target.value);
                    setValidationErrors({ ...validationErrors, encryptionPassword: '' });
                  }}
                  placeholder="Enter encryption password"
                  disabled={loading}
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  className="toggle-password"
                  onClick={() => setShowEpass(!showEpass)}
                  title={showEpass ? 'Hide password' : 'Show password'}
                >
                  {showEpass ? '👁️' : '👁️‍🗨️'}
                </button>
              </div>
              {validationErrors.encryptionPassword && (
                <span className="error-message">{validationErrors.encryptionPassword}</span>
              )}
              <small className="password-info">
                Used for AES-256 message encryption
              </small>
            </div>

            {/* Login Button */}
            <button
              type="submit"
              className="w3-btn w3-btn-blue-grey login-btn"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="spinner"></span>
                  Logging in...
                </>
              ) : (
                'Login'
              )}
            </button>

            {/* Demo Login Button */}
            <button
              type="button"
              className="w3-btn demo-btn"
              onClick={handleDemoLogin}
              disabled={loading}
            >
              Use Demo Credentials (admin/admin)
            </button>
          </form>

          {/* Footer Info */}
          <footer className="w3-container login-footer">
            <p>🛡️ Secure • 🔐 Encrypted • 🔒 Private</p>
          </footer>
        </div>

        {/* Info Section */}
        <div className="login-info">
          <div className="info-card">
            <h3>🖼️ Image Steganography</h3>
            <p>Hide encrypted messages in images using LSB encoding across 2 images.</p>
          </div>
          <div className="info-card">
            <h3>🔊 Audio Steganography</h3>
            <p>Embed encrypted messages in WAV audio files securely.</p>
          </div>
          <div className="info-card">
            <h3>🔐 AES-256 Encryption</h3>
            <p>Military-grade encryption with PBKDF2 key derivation.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
