import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/apiService';
import FaceEnrollment from './FaceEnrollment';
import '../css/w3.css';
import './Components.css';

function FaceEnrollmentPage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [enrollmentComplete, setEnrollmentComplete] = useState(false);

  useEffect(() => {
    const user = authService.getCurrentUser();
    if (user) {
      setUsername(user);
    }
  }, []);

  const handleEnrollmentComplete = (success) => {
    if (success) {
      setEnrollmentComplete(true);
      // Auto-redirect after 3 seconds
      setTimeout(() => {
        navigate('/home');
      }, 3000);
    }
  };

  if (enrollmentComplete) {
    return (
      <div className="w3-container">
        <div className="w3-card-4 w3-margin" style={{
          backgroundColor: '#d4edda',
          border: '3px solid #28a745',
          borderRadius: '8px',
          padding: '30px',
          textAlign: 'center'
        }}>
          <h1 style={{ color: '#155724' }}>✅ Face Enrollment Successful!</h1>
          <p style={{ fontSize: '16px', color: '#155724' }}>
            Your face has been registered successfully.
          </p>
          <p style={{ fontSize: '14px', color: '#155724' }}>
            Redirecting to home page in 3 seconds...
          </p>
          <button
            className="w3-btn w3-green"
            onClick={() => navigate('/home')}
            style={{ marginTop: '10px' }}
          >
            Go to Home Now
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="w3-container">
      <div className="w3-card-4 w3-margin">
        <header className="w3-container w3-blue">
          <h1>👤 Face Enrollment</h1>
        </header>

        <div className="w3-container w3-margin">
          <div style={{
            backgroundColor: '#e3f2fd',
            border: '1px solid #2196f3',
            borderRadius: '4px',
            padding: '15px',
            marginBottom: '20px'
          }}>
            <h3 style={{ color: '#1565c0', marginTop: 0 }}>📝 Instructions</h3>
            <ul style={{ marginBottom: 0 }}>
              <li>Make sure you're in a well-lit area</li>
              <li>Position your face clearly in front of the camera</li>
              <li>Ensure your entire face is visible</li>
              <li>Click "Start Camera" to begin</li>
              <li>Click "Capture Face" when ready</li>
              <li>Review the captured image</li>
              <li>Click "Enroll" to save your face</li>
            </ul>
          </div>

          {username && (
            <p style={{ fontSize: '14px', color: '#666' }}>
              <strong>👤 Username:</strong> {username}
            </p>
          )}

          <FaceEnrollment
            username={username}
            onEnrollmentComplete={handleEnrollmentComplete}
          />
        </div>

        <footer className="w3-container w3-blue">
          <h5></h5>
        </footer>
      </div>

      {/* Information Section */}
      <div className="w3-card-4 w3-margin" style={{ marginTop: '30px' }}>
        <header className="w3-container w3-light-grey">
          <h3>ℹ️ About Face Enrollment</h3>
        </header>
        <div className="w3-container" style={{ padding: '20px' }}>
          <p>
            <strong>What is Face Enrollment?</strong>
          </p>
          <p>
            Face enrollment registers your facial biometrics in our system. This allows you to use face verification as an additional security layer when decrypting messages.
          </p>

          <p>
            <strong>How does it work?</strong>
          </p>
          <ul>
            <li>Your face is captured using your webcam</li>
            <li>Advanced algorithms extract unique facial features (encoding)</li>
            <li>This encoding is stored securely in the database</li>
            <li>Later, when you decrypt, your face is verified against this encoding</li>
          </ul>

          <p>
            <strong>Is it optional?</strong>
          </p>
          <p>
            Yes! Face enrollment is completely optional. You can use the system with just a password. Face verification adds an extra layer of security if you choose to use it.
          </p>

          <p>
            <strong>Privacy & Security</strong>
          </p>
          <ul>
            <li>Your facial encoding is encrypted and stored securely</li>
            <li>No image files are permanently stored - only the encrypted encoding</li>
            <li>You can delete your face data anytime</li>
            <li>Face data is never shared or transmitted outside the system</li>
          </ul>

          <p style={{ fontSize: '12px', color: '#999', marginTop: '20px' }}>
            💡 Tip: For best results, enroll in good lighting conditions with multiple poses for improved accuracy.
          </p>
        </div>
      </div>
    </div>
  );
}

export default FaceEnrollmentPage;
