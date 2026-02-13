import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import '../css/FaceAuth.css';

const FaceEnrollment = ({ onEnrollmentComplete, username }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [cameraActive, setCameraActive] = useState(false);
  const [capturedImage, setCapturedImage] = useState(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  // Initialize camera
  useEffect(() => {
    if (cameraActive) {
      startCamera();
    } else {
      stopCamera();
    }

    return () => stopCamera();
  }, [cameraActive]);

  const startCamera = async () => {
    try {
      console.log('🎥 Starting camera...');
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } },
        audio: false
      });

      console.log('✓ Camera stream acquired');
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      console.error('❌ Camera error:', err);
      console.error('Error type:', err.name);
      console.error('Error message:', err.message);

      let errorMessage = 'Unable to access camera. Please check permissions.';
      
      if (err.name === 'NotAllowedError') {
        errorMessage = '❌ Camera permission DENIED. You need to grant camera access in browser settings.';
      } else if (err.name === 'NotFoundError') {
        errorMessage = '❌ No camera found. Check that your camera is connected and not in use by another app.';
      } else if (err.name === 'NotReadableError') {
        errorMessage = '❌ Camera is in use by another application. Close other apps using the camera and try again.';
      } else if (err.name === 'SecurityError') {
        errorMessage = '❌ Security error: Camera requires HTTPS or localhost. You may need to refresh the page.';
      } else if (err.name === 'TypeError') {
        errorMessage = '❌ Camera API not available. Your browser may not support camera access.';
      }
      
      setError(errorMessage);
      setCameraActive(false);
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      videoRef.current.srcObject.getTracks().forEach(track => track.stop());
    }
  };

  const captureFrame = () => {
    if (videoRef.current && canvasRef.current) {
      const context = canvasRef.current.getContext('2d');
      canvasRef.current.width = videoRef.current.videoWidth;
      canvasRef.current.height = videoRef.current.videoHeight;
      context.drawImage(videoRef.current, 0, 0);

      canvasRef.current.toBlob((blob) => {
        setCapturedImage(blob);
        setCameraActive(false);
        setError(null);
      });
    }
  };

  const handleEnroll = async () => {
    if (!capturedImage) {
      setError('Please capture a face image first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('face_image', capturedImage, 'face.png');

      const response = await axios.post('/api/face/enroll', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setSuccess(true);
      setLoading(false);
      setCapturedImage(null);

      // Call parent callback
      setTimeout(() => {
        onEnrollmentComplete(true);
      }, 2000);
    } catch (err) {
      setError(
        err.response?.data?.error ||
        err.response?.data?.message ||
        'Face enrollment failed'
      );
      setLoading(false);
    }
  };

  const retryCapture = () => {
    setCapturedImage(null);
    setCameraActive(true);
  };

  return (
    <div className="face-enrollment">
      <h2>Enroll Face for Authentication</h2>
      <p className="info-text">
        Capture a clear image of your face for authentication. Good lighting is recommended.
      </p>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">✓ Face enrolled successfully!</div>}

      {!capturedImage ? (
        <>
          {!cameraActive ? (
            <button
              className="btn btn-primary"
              onClick={() => setCameraActive(true)}
              disabled={loading || success}
            >
              📷 Start Camera
            </button>
          ) : (
            <div className="camera-container">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                style={{ width: '100%', borderRadius: '8px' }}
              />
              <div className="camera-controls">
                <button
                  className="btn btn-success"
                  onClick={captureFrame}
                  disabled={loading}
                >
                  📸 Capture Face
                </button>
                <button
                  className="btn btn-secondary"
                  onClick={() => setCameraActive(false)}
                  disabled={loading}
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="preview-container">
          <canvas
            ref={canvasRef}
            style={{ display: 'none' }}
          />
          <div className="image-preview">
            <h3>Face Preview</h3>
            <img
              src={URL.createObjectURL(capturedImage)}
              alt="Captured face"
              style={{ maxWidth: '300px', borderRadius: '8px' }}
            />
          </div>
          <div className="action-buttons">
            <button
              className="btn btn-success"
              onClick={handleEnroll}
              disabled={loading}
            >
              {loading ? '⏳ Enrolling...' : '✓ Confirm Enrollment'}
            </button>
            <button
              className="btn btn-secondary"
              onClick={retryCapture}
              disabled={loading}
            >
              🔄 Retake Photo
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default FaceEnrollment;
