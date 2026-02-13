import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { contentService } from '../services/apiService';
import '../css/w3.css';

function Home() {
  const navigate = useNavigate();
  const [content, setContent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchContent = async () => {
      try {
        const data = await contentService.getHome();
        setContent(data);
      } catch (err) {
        setError('Failed to load home content');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchContent();
  }, []);

  if (loading) return <div className="w3-container"><p>Loading...</p></div>;
  if (error) return <div className="w3-container"><p className="error">{error}</p></div>;

  return (
    <div className="w3-container">
      <img src="/images/bgImage.jpg" alt="Background" style={{ width: '100%', marginBottom: '20px' }} />

      {/* Introduction Card */}
      <div className="w3-card-4 w3-margin">
        <header className="w3-container w3-blue">
          <h1>{content?.introduction?.title}</h1>
        </header>
        <div className="w3-container">
          <p>{content?.introduction?.text}</p>
        </div>
        <footer className="w3-container w3-blue">
          <h5></h5>
        </footer>
      </div>

      {/* About Card */}
      <div className="w3-card-4 w3-margin">
        <header className="w3-container w3-blue">
          <h1>{content?.about?.title}</h1>
        </header>
        <div className="w3-container">
          <p>{content?.about?.text}</p>
        </div>
        <footer className="w3-container w3-blue">
          <h5></h5>
        </footer>
      </div>

      {/* Face Enrollment Card */}
      <div className="w3-card-4 w3-margin" style={{ borderTop: '4px solid #ff9800' }}>
        <header className="w3-container" style={{ backgroundColor: '#fff3e0' }}>
          <h2 style={{ color: '#e65100', margin: '10px 0' }}>👤 Face Enrollment (Optional)</h2>
        </header>
        <div className="w3-container" style={{ padding: '20px' }}>
          <p>
            Enhance your security by enrolling your face! Face enrollment is <strong>completely optional</strong> 
            and allows you to use facial biometrics as an additional authentication layer.
          </p>
          
          <div style={{
            backgroundColor: '#e8f5e9',
            border: '1px solid #4caf50',
            borderRadius: '4px',
            padding: '15px',
            marginBottom: '15px'
          }}>
            <h4 style={{ marginTop: 0, color: '#2e7d32' }}>✨ Benefits:</h4>
            <ul style={{ marginBottom: 0 }}>
              <li>Extra security layer - password + face verification</li>
              <li>Quick and easy enrollment process</li>
              <li>Works with any webcam</li>
              <li>Can be disabled anytime</li>
              <li>Your privacy is protected</li>
            </ul>
          </div>

          <p style={{ fontSize: '14px', color: '#666' }}>
            <strong>How it works:</strong> Capture your face using your webcam, and the system will save a secure 
            facial encoding. Later, when you decrypt messages, you can verify with your face for added security.
          </p>

          <button
            className="w3-btn"
            onClick={() => navigate('/face-enrollment')}
            style={{
              backgroundColor: '#ff9800',
              color: 'white',
              padding: '12px 24px',
              fontSize: '16px',
              borderRadius: '4px',
              border: 'none',
              cursor: 'pointer'
            }}
          >
            👤 Enroll Your Face Now
          </button>
          
          <p style={{ fontSize: '12px', color: '#999', marginTop: '15px' }}>
            💡 Enrollment takes less than a minute. You can skip this and just use the system with a password.
          </p>
        </div>
        <footer className="w3-container" style={{ backgroundColor: '#fff3e0' }}>
          <small style={{ color: '#666' }}>Optional security feature</small>
        </footer>
      </div>

      {/* Architecture Diagram */}
      <div className="w3-container w3-center">
        <h2>{content?.architecture?.title}</h2>
        <img src={content?.architecture?.image} alt="Architecture Diagram" style={{ width: '100%' }} />
        <p>Figure 1</p>
      </div>
    </div>
  );
}

export default Home;
