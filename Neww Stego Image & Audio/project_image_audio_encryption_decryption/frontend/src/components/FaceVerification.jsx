import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import '../css/FaceAuth.css';

const FaceVerification = ({ onVerificationComplete, username }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [cameraActive, setCameraActive] = useState(false);
  const [capturedImage, setCapturedImage] = useState(null);
  const [matchDetails, setMatchDetails] = useState(null);
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
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } },
        audio: false
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      setError('Unable to access camera. Please check permissions.');
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

  const handleVerify = async () => {
    if (!capturedImage) {
      setError('Please capture a face image first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('face_image', capturedImage, 'face.png');

      const response = await axios.post('/api/face/verify', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setMatchDetails({
        distance: response.data.distance,
        tolerance: response.data.tolerance,
        verified: response.data.success
      });

      if (response.data.success) {
        setSuccess(true);
        setTimeout(() => {
          onVerificationComplete(true);
        }, 2000);
      } else {
        setError('Face does not match. Please try again.');
      }

      setLoading(false);
    } catch (err) {
      const errorMsg = err.response?.data?.message || 
                       err.response?.data?.error || 
                       'Face verification failed';
      setError(errorMsg);
      setLoading(false);
    }
  };

  const retryCapture = () => {
    setCapturedImage(null);
    setMatchDetails(null);
    setCameraActive(true);
  };

  return (
    <div className="face-verification">
      <h2>Verify Your Face</h2>
      <p className="info-text">
        Look directly at the camera for the best results.
      </p>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">✓ Face verified successfully!</div>}

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
          <canvas ref={canvasRef} style={{ display: 'none' }} />
          <div className="image-preview">
            <h3>Face Preview</h3>
            <img
              src={URL.createObjectURL(capturedImage)}
              alt="Captured face"
              style={{ maxWidth: '300px', borderRadius: '8px' }}
            />
          </div>

          {matchDetails && (
            <div className={`match-details ${matchDetails.verified ? 'success' : 'failed'}`}>
              <p>
                <strong>Match Distance:</strong> {matchDetails.distance.toFixed(4)}
              </p>
              <p>
                <strong>Tolerance:</strong> {matchDetails.tolerance}
              </p>
              <p>
                {matchDetails.verified ? '✓ Face matches!' : '✗ Face does not match'}
              </p>
            </div>
          )}

          <div className="action-buttons">
            <button
              className="btn btn-success"
              onClick={handleVerify}
              disabled={loading}
            >
              {loading ? '⏳ Verifying...' : '✓ Verify Face'}
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

export default FaceVerification;
