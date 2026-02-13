/**
 * Login Component - Professional Steganography Application
 * 
 * Features:
 * - Modern gradient background
 * - Professional form design
 * - Password visibility toggle
 * - Form validation
 * - Loading states with spinner
 * - Error handling with styled messages
 * - Demo credentials section
 * - Feature showcase cards
 * - Fully responsive design
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/apiService';
import '../css/w3.css';
import '../css/Professional.css';
import '../css/Login.css';

function Login() {
  // Form State
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    epass: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showEpass, setShowEpass] = useState(false);

  // UI State
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [validationErrors, setValidationErrors] = useState({});

  // Navigation
  const navigate = useNavigate();

  // Check if already logged in (runs once on mount)
  useEffect(() => {
    let isMounted = true;
    
    const checkAuth = async () => {
      if (!isMounted) return;
      
      try {
        // Create a timeout promise
        const timeoutPromise = new Promise((_, reject) =>
          setTimeout(() => reject(new Error('Session check timeout')), 3000)
        );
        
        const result = await Promise.race([authService.getSession(), timeoutPromise]);
        
        if (isMounted && result?.authenticated) {
          navigate('/home');
        }
      } catch (err) {
        // Not authenticated or backend unavailable, stay on login
        // Error is silent - user can proceed to login
      }
    };
    
    checkAuth();
    
    // Cleanup on unmount
    return () => {
      isMounted = false;
    };
  }, []); // Empty dependency array - runs only once on mount

  /**
   * Validate form inputs
   */
  const validateForm = () => {
    const errors = {};

    if (!formData.username.trim()) {
      errors.username = 'Username is required';
    } else if (formData.username.trim().length < 3) {
      errors.username = 'Username must be at least 3 characters';
    }

    if (!formData.password.trim()) {
      errors.password = 'Password is required';
    } else if (formData.password.trim().length < 3) {
      errors.password = 'Password must be at least 3 characters';
    }

    if (!formData.epass.trim()) {
      errors.epass = 'Encryption password is required';
    } else if (formData.epass.trim().length < 3) {
      errors.epass = 'Encryption password must be at least 3 characters';
    }

    return errors;
  };

  /**
   * Handle input change
   */
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Clear validation error for this field
    if (validationErrors[name]) {
      setValidationErrors((prev) => ({
        ...prev,
        [name]: '',
      }));
    }
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

    setError('');
    setLoading(true);

    try {
      const result = await authService.login(
        formData.username.trim(),
        formData.password.trim(),
        formData.epass.trim()
      );

      if (result.success) {
        // Success - redirect after brief delay
        setTimeout(() => {
          navigate('/home');
        }, 800);
      } else {
        setError(result.error || 'Login failed. Please try again.');
      }
    } catch (err) {
      if (err.code === 'ECONNABORTED') {
        setError('Server is not responding. Please ensure the backend server is running on port 5001.');
      } else if (err.message === 'Network Error') {
        setError('Cannot connect to server. Is the backend running?');
      } else {
        const errorMessage = err.response?.data?.error || err.message || 'Connection error. Please check the backend server.';
        setError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  /**
   * Apply demo credentials
   */
  const applyDemoCredentials = () => {
    setFormData({
      username: 'admin',
      password: 'admin',
      epass: 'admin',
    });
    setValidationErrors({});
    setError('');
  };

  return (
    <div className="login-container">
      <div className="login-wrapper">
        {/* Login Card */}
        <div className="login-card">
          {/* Header with gradient background */}
          <div className="login-header">
            <h1>🔐 Steganography</h1>
            <p className="login-subtitle">Secure Message Hiding & Encryption</p>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="login-alert-container">
              <div className="alert alert-error">
                <strong>⚠️ Error:</strong> {error}
              </div>
            </div>
          )}

          {/* Login Form */}
          <form className="login-form" onSubmit={handleSubmit}>
            {/* Username Field */}
            <div className="form-group">
              <label htmlFor="username">
                <span className="label-icon">👤</span> Username
              </label>
              <input
                id="username"
                type="text"
                name="username"
                className={`w3-input ${validationErrors.username ? 'input-error' : ''}`}
                value={formData.username}
                onChange={handleChange}
                placeholder="Enter username"
                disabled={loading}
                autoComplete="username"
              />
              {validationErrors.username && (
                <span className="error-message">{validationErrors.username}</span>
              )}
            </div>

            {/* Password Field */}
            <div className="form-group">
              <label htmlFor="password">
                <span className="label-icon">🔒</span> Login Password
              </label>
              <div className="password-input-wrapper">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  className={`w3-input ${validationErrors.password ? 'input-error' : ''}`}
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="Enter password"
                  disabled={loading}
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  className="toggle-password-btn"
                  onClick={() => setShowPassword(!showPassword)}
                  title={showPassword ? 'Hide password' : 'Show password'}
                  disabled={loading}
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
              <label htmlFor="epass">
                <span className="label-icon">🔑</span> Encryption Password
              </label>
              <div className="password-input-wrapper">
                <input
                  id="epass"
                  type={showEpass ? 'text' : 'password'}
                  name="epass"
                  className={`w3-input ${validationErrors.epass ? 'input-error' : ''}`}
                  value={formData.epass}
                  onChange={handleChange}
                  placeholder="For AES-256 encryption"
                  disabled={loading}
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  className="toggle-password-btn"
                  onClick={() => setShowEpass(!showEpass)}
                  title={showEpass ? 'Hide password' : 'Show password'}
                  disabled={loading}
                >
                  {showEpass ? '👁️' : '👁️‍🗨️'}
                </button>
              </div>
              {validationErrors.epass && (
                <span className="error-message">{validationErrors.epass}</span>
              )}
              <small className="password-hint">
                ℹ️ Used for AES-256-CTR encryption of messages
              </small>
            </div>

            {/* Login Button */}
            <button
              type="submit"
              className="login-btn"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="spinner"></span>
                  Authenticating...
                </>
              ) : (
                '🚀 Login'
              )}
            </button>

            {/* Demo Login Button */}
            <button
              type="button"
              className="demo-btn"
              onClick={applyDemoCredentials}
              disabled={loading}
            >
              📝 Use Demo Credentials
            </button>
          </form>

          {/* Footer */}
          <div className="login-footer">
            <p>🛡️ Secure • 🔐 Encrypted • 🔒 Private</p>
          </div>
        </div>

        {/* Info Cards */}
        <div className="login-info">
          <div className="info-card">
            <div className="info-icon">🖼️</div>
            <h3>Image Steganography</h3>
            <p>Hide encrypted messages in images using LSB encoding across 2 images for maximum capacity.</p>
          </div>
          <div className="info-card">
            <div className="info-icon">🔊</div>
            <h3>Audio Steganography</h3>
            <p>Embed encrypted messages in WAV audio files with LSB steganography technique.</p>
          </div>
          <div className="info-card">
            <div className="info-icon">🔐</div>
            <h3>Military-Grade Encryption</h3>
            <p>AES-256-CTR encryption mode with PBKDF2 key derivation for maximum security.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
