import React, { useState, useEffect } from 'react';
import { fileService } from '../services/apiService';
import FaceAuth from './FaceAuth';
import '../css/w3.css';
import './Components.css';

function Decryption() {
  const [cipherText, setCipherText] = useState('');
  const [password, setPassword] = useState('');
  const [decryptedMessage, setDecryptedMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [faceAuthRequired, setFaceAuthRequired] = useState(false);
  const [faceVerified, setFaceVerified] = useState(false);
  const [username, setUsername] = useState('');
  const [faceCheckDone, setFaceCheckDone] = useState(false);

  // Check face authentication status on component mount
  useEffect(() => {
    checkFaceStatus();
  }, []);

  const checkFaceStatus = async () => {
    try {
      console.log('Checking face enrollment status...');
      const response = await fileService.checkFaceEnrollment();
      console.log('Face enrollment response:', response.data);
      
      // If face auth is disabled, skip it
      if (response.data.face_auth_disabled) {
        console.log('✓ Face authentication is disabled on backend - skipping');
        setFaceAuthRequired(false);
        setFaceVerified(false);
        setFaceCheckDone(true);
        return;
      }
      
      setFaceAuthRequired(response.data.face_required);
      setFaceVerified(response.data.face_enrolled && response.data.stats?.last_authenticated);
      setUsername(response.data.username);
    } catch (err) {
      // Face auth check failed - continue without it
      console.log('⚠ Face authentication check failed - continuing without face auth:', err.message);
      console.log('This is normal if face recognition is not configured.');
      setFaceAuthRequired(false);
      setFaceVerified(false);
    } finally {
      setFaceCheckDone(true);
    }
  };

  const handleDecrypt = async (e) => {
    e.preventDefault();
    
    if (!cipherText.trim()) {
      setError('Please enter cipher text');
      return;
    }
    
    if (!password.trim()) {
      setError('Please enter encryption password');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');
    setDecryptedMessage('');

    try {
      console.log('🔓 Decrypting message...');
      console.log('Cipher length:', cipherText.length);
      console.log('Password length:', password.length);
      
      const result = await fileService.decryptMessage(cipherText, password);
      console.log('✓ Full decryption response:', result);
      console.log('Response type:', typeof result);
      console.log('Response keys:', Object.keys(result || {}));
      console.log('result.success:', result?.success);
      console.log('result.message:', result?.message);
      console.log('result.plaintext:', result?.plaintext);
      
      if (result && result.success) {
        const message = result.message || result.plaintext || '';
        console.log('✓ Decryption successful, message:', message);
        console.log('Message length:', message.length);
        
        // Force state update
        setDecryptedMessage(message);
        setSuccess('✓ Message decrypted successfully!');
        
        // Show visual confirmation
        alert('✅ Message decrypted successfully! Scroll down to see it.');
        
        // Verify state was set
        setTimeout(() => {
          console.log('Verifying decrypted message in state...');
        }, 100);
      } else {
        const errorMsg = result?.error || result?.message || 'Decryption failed';
        console.error('✗ Decryption failed:', errorMsg);
        setError(errorMsg);
      }
    } catch (err) {
      console.error('✗ Decryption error:', err);
      console.error('Error response:', err.response?.data);
      console.error('Error message:', err.message);
      
      const errorMsg = err.response?.data?.error || 
                       err.response?.data?.message ||
                       err.message ||
                       'An error occurred during decryption';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleFaceAuthComplete = (faceStatus) => {
    if (faceStatus.verified) {
      setFaceVerified(true);
      setError('');
    }
  };

  // Show nothing while checking face status
  if (!faceCheckDone) {
    return null;
  }

  return (
    <div className="w3-container">
      {/* Debug Display: Show decryptedMessage state */}
      <div style={{
        display: decryptedMessage ? 'block' : 'none',
        backgroundColor: '#fffacd',
        border: '2px dashed #ff9800',
        borderRadius: '4px',
        padding: '10px',
        marginBottom: '10px',
        fontSize: '12px',
        color: '#333'
      }}>
        <strong>🐛 DEBUG:</strong> Message state exists: {decryptedMessage ? `YES (${decryptedMessage.length} chars)` : 'NO'}
      </div>

      {/* ALWAYS SHOW MESSAGE BOX IF MESSAGE EXISTS - at the very top */}
      {decryptedMessage && (
        <div style={{
          position: 'relative',
          zIndex: 1000,
          backgroundColor: '#d4edda',
          border: '3px solid #28a745',
          borderRadius: '8px',
          padding: '20px',
          marginBottom: '20px',
          marginTop: '10px'
        }}>
          <h2 style={{ color: '#155724', marginTop: 0 }}>✅ DECRYPTED MESSAGE</h2>
          <div style={{
            backgroundColor: '#ffffff',
            border: '2px solid #28a745',
            borderRadius: '6px',
            padding: '15px',
            marginBottom: '10px',
            fontSize: '16px',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
            fontFamily: 'monospace',
            minHeight: '50px',
            maxHeight: '300px',
            overflowY: 'auto'
          }}>
            {decryptedMessage}
          </div>
          <div style={{ fontSize: '12px', color: '#155724', marginBottom: '10px' }}>
            📊 Size: {decryptedMessage.length} characters
          </div>
          <button 
            onClick={() => {
              navigator.clipboard.writeText(decryptedMessage);
              alert('✓ Copied to clipboard');
            }}
            style={{
              backgroundColor: '#28a745',
              color: 'white',
              border: 'none',
              padding: '10px 20px',
              borderRadius: '4px',
              cursor: 'pointer',
              marginRight: '10px',
              fontSize: '14px'
            }}
          >
            📋 Copy
          </button>
          <button 
            onClick={() => {
              setDecryptedMessage('');
              setCipherText('');
              setPassword('');
              setSuccess('');
            }}
            style={{
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              padding: '10px 20px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '14px'
            }}
          >
            🔄 Clear
          </button>
        </div>
      )}

      {/* Face Authentication Component */}
      {faceAuthRequired && !faceVerified && (
        <div style={{
          backgroundColor: '#fff3cd',
          border: '1px solid #ffc107',
          borderRadius: '4px',
          padding: '15px',
          marginBottom: '20px'
        }}>
          <FaceAuth
            username={username}
            onAuthComplete={handleFaceAuthComplete}
            showModal={false}
          />
        </div>
      )}

      {/* Face Verification Success Banner */}
      {faceAuthRequired && faceVerified && (
        <div style={{
          backgroundColor: '#d4edda',
          border: '1px solid #c3e6cb',
          borderRadius: '4px',
          padding: '15px',
          marginBottom: '20px',
          color: '#155724'
        }}>
          <strong>✓ Face Verified</strong> - You are authenticated for decryption
        </div>
      )}

      <div className="w3-card-4 w3-margin">
        <header className="w3-container w3-blue">
          <h1>Decrypt Message</h1>
        </header>

        <form className="w3-container w3-margin" onSubmit={handleDecrypt}>
          <label className="w3-text-teal">
            <b>Cipher Text</b>
          </label>
          <textarea
            className="w3-input w3-border w3-light-grey"
            rows="10"
            cols="47"
            value={cipherText}
            onChange={(e) => setCipherText(e.target.value)}
            placeholder="Paste your cipher text here..!!"
          ></textarea>
          <br />

          <label className="w3-text-teal">
            <b>Encryption Password</b>
          </label>
          <input
            className="w3-input w3-border w3-light-grey"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter the encryption password"
          />
          <br />

          <button 
            className="w3-btn w3-blue-grey" 
            type="submit" 
            disabled={loading || (faceAuthRequired && !faceVerified)}
          >
            {loading ? 'Decrypting...' : 'Decrypt'}
          </button>

          {error && <p style={{ color: '#d32f2f', marginTop: '10px' }}><strong>Error:</strong> {error}</p>}
          {success && <p style={{ color: '#388e3c', marginTop: '10px' }}><strong>Success:</strong> {success}</p>}
        </form>

        <footer className="w3-container w3-blue">
          <h5></h5>
        </footer>
      </div>

      {decryptedMessage && (
        <div className="w3-card-4 w3-margin" style={{ backgroundColor: '#f0f8f0', marginTop: '30px' }}>
          <header className="w3-container w3-green">
            <h1>📝 Message Details</h1>
          </header>
          <div className="w3-container" style={{ padding: '20px' }}>
            <p><strong>✓ Decryption complete.</strong> See the green box above for your message.</p>
            <p>Message statistics:</p>
            <ul>
              <li><strong>Length:</strong> {decryptedMessage.length} characters</li>
              <li><strong>Type:</strong> UTF-8 Text</li>
              <li><strong>Status:</strong> Successfully decrypted</li>
            </ul>
          </div>
          <footer className="w3-container w3-green">
            <small>✓ Ready to use</small>
          </footer>
        </div>
      )}
    </div>
  );
}

export default Decryption;
