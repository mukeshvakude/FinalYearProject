import React, { useState, useEffect } from 'react';
import axios from 'axios';
import FaceEnrollment from './FaceEnrollment';
import FaceVerification from './FaceVerification';
import '../css/FaceAuth.css';

const FaceAuth = ({ username, onAuthComplete, showModal = true }) => {
  const [enrollmentStatus, setEnrollmentStatus] = useState(null);
  const [verified, setVerified] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    // Set a timeout to prevent infinite loading
    const timeout = setTimeout(() => {
      if (loading) {
        setLoading(false);
        console.log('Face auth check timed out - disabling face auth');
        setError(null); // Don't show error, just disable silently
      }
    }, 5000);

    checkFaceEnrollment();
    return () => clearTimeout(timeout);
  }, []);

  const checkFaceEnrollment = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/face/check-enrollment', {
        timeout: 3000 // 3 second timeout
      });
      
      // If face auth is disabled on backend, don't show anything
      if (response.data.face_auth_disabled) {
        console.log('✓ Face authentication is disabled on backend');
        setEnrollmentStatus(null); // Disable face auth UI
        setStats(null);
        setLoading(false);
        return;
      }
      
      setEnrollmentStatus(response.data.face_enrolled);
      setStats(response.data.stats);
      setError(null);
    } catch (err) {
      // Face auth is not critical - continue without it
      console.log('Face enrollment status check failed (non-critical):', err.message);
      setEnrollmentStatus(null); // Disable face auth UI on error
      setStats(null);
    } finally {
      setLoading(false);
    }
  };

  const handleEnrollmentComplete = (success) => {
    if (success) {
      setEnrollmentStatus(true);
      checkFaceEnrollment(); // Refresh stats
      if (onAuthComplete) {
        onAuthComplete({ enrolled: true, verified: false });
      }
    }
  };

  const handleVerificationComplete = (success) => {
    if (success) {
      setVerified(true);
      if (onAuthComplete) {
        onAuthComplete({ enrolled: true, verified: true });
      }
    }
  };

  const handleDeleteFace = async () => {
    if (window.confirm('Are you sure you want to delete your face enrollment? You will need to re-enroll.')) {
      try {
        await axios.post('/api/face/delete');
        setEnrollmentStatus(false);
        setVerified(false);
        setStats(null);
      } catch (err) {
        setError('Failed to delete face enrollment');
      }
    }
  };

  // If enrollment status is null and not loading, don't render anything
  // (face auth is disabled on backend)
  if (enrollmentStatus === null && !loading) {
    return null;
  }

  // Show nothing while checking (max 5 seconds)
  if (loading) {
    return (
      <div className="face-enrollment">
        <p style={{ textAlign: 'center' }}>Checking face authentication...</p>
      </div>
    );
  }

  // Main content
  const content = (
    <>
      {error && <div className="error-message">⚠ {error}</div>}

      {/* Enrollment Status Badge */}
      {enrollmentStatus !== null && (
        <div className={`face-auth-status ${enrollmentStatus ? 'enrolled' : 'not-enrolled'}`}>
          {enrollmentStatus ? '✓ Face Enrolled' : '✗ Face Not Enrolled'}
        </div>
      )}

      {/* Verification Status Badge */}
      {enrollmentStatus && (
        <div className={`face-auth-status ${verified ? 'verified' : 'not-verified'}`}>
          {verified ? '✓ Face Verified' : '○ Face Not Yet Verified'}
        </div>
      )}

      {/* Stats Display */}
      {stats && enrollmentStatus && (
        <div className="face-stats-card">
          <h4>Authentication History</h4>
          <p>
            <span className="label">Enrolled:</span>
            <span className="value">{new Date(stats.enrolled).toLocaleDateString()}</span>
          </p>
          <p>
            <span className="label">Last Verified:</span>
            <span className="value">
              {stats.last_authenticated
                ? new Date(stats.last_authenticated).toLocaleString()
                : 'Never'}
            </span>
          </p>
          <p>
            <span className="label">Total Verifications:</span>
            <span className="value">{stats.authentication_count}</span>
          </p>
        </div>
      )}

      {/* Enrollment Flow */}
      {enrollmentStatus === false && (
        <FaceEnrollment
          onEnrollmentComplete={handleEnrollmentComplete}
          username={username}
        />
      )}

      {/* Verification Flow */}
      {enrollmentStatus === true && !verified && (
        <FaceVerification
          onVerificationComplete={handleVerificationComplete}
          username={username}
        />
      )}

      {/* Success State */}
      {enrollmentStatus === true && verified && (
        <div className="face-enrollment" style={{ textAlign: 'center' }}>
          <h2>✓ Face Authenticated</h2>
          <p style={{ fontSize: '16px', marginBottom: '20px' }}>
            You are now verified and can proceed with decryption.
          </p>
          <button
            className="btn btn-secondary"
            onClick={handleDeleteFace}
          >
            🔄 Re-enroll Face
          </button>
        </div>
      )}
    </>
  );

  // Render as modal or inline
  if (showModal && enrollmentStatus === false) {
    return (
      <div className="face-auth-modal">
        <div className="face-auth-content">
          {content}
        </div>
      </div>
    );
  }

  return content;
};

export default FaceAuth;
