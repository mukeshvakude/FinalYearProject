import React, { useState, useRef, useEffect } from 'react';
import { fileService } from '../services/apiService';
import '../css/w3.css';
import './Components.css';

function Encryption() {
  const [filetype, setFiletype] = useState('image');
  const [images, setImages] = useState({ photo: null, photo1: null });
  const [audioFile, setAudioFile] = useState(null);
  const [message, setMessage] = useState('');
  const [cipher, setCipher] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [audioList, setAudioList] = useState([]);
  const [audioListLoading, setAudioListLoading] = useState(false);
  const fileInputRef1 = useRef(null);
  const fileInputRef2 = useRef(null);
  const audioInputRef = useRef(null);

  useEffect(() => {
    fetchAudioList();
  }, []);

  const fetchAudioList = async () => {
    setAudioListLoading(true);
    try {
      const response = await fileService.getAudioList();
      if (response.success) {
        setAudioList(response.audio_files);
      }
    } catch (err) {
      console.error('Failed to fetch audio list:', err);
    } finally {
      setAudioListLoading(false);
    }
  };

  const handleFiletypeChange = (e) => {
    const newType = e.target.value;
    setFiletype(newType);
    setError('');
    setSuccess('');
    setCipher('');
  };

  const handleImageUpload = async (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const formData = new FormData();
    formData.append('filetype', 'image');
    
    if (e.target === fileInputRef1.current && fileInputRef1.current.files.length > 0) {
      formData.append('photo', fileInputRef1.current.files[0]);
      setImages(prev => ({ ...prev, photo: fileInputRef1.current.files[0].name }));
    }
    
    if (fileInputRef2.current && fileInputRef2.current.files.length > 0) {
      formData.append('photo1', fileInputRef2.current.files[0]);
      setImages(prev => ({ ...prev, photo1: fileInputRef2.current.files[0].name }));
    }

    if (formData.getAll('photo').length === 0 && formData.getAll('photo1').length === 0) {
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const result = await fileService.uploadFiles('image', formData);
      if (result.success) {
        setSuccess(result.message);
      } else {
        setError(result.error || 'Upload failed');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const handleAudioUpload = async (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const formData = new FormData();
    formData.append('filetype', 'audio');
    formData.append('audiofile', files[0]);
    setAudioFile(files[0].name);

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const result = await fileService.uploadFiles('audio', formData);
      if (result.success) {
        setSuccess(result.message);
      } else {
        setError(result.error || 'Upload failed');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const handleHideMessage = async (e) => {
    e.preventDefault();

    if (!message.trim()) {
      setError('Please enter a message');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const result = await fileService.hideMessage(message, filetype);
      if (result.success) {
        setCipher(result.cipher);
        setSuccess(result.message);
      } else {
        setError(result.error || 'Failed to hide message');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w3-container">
      {/* Hide Message Card */}
      <div className="w3-card-4 w3-margin">
        <header className="w3-container w3-blue">
          <h1>Hide Message</h1>
        </header>

        {/* Image Preview Section */}
        {filetype === 'image' && (
          <div id="image-blocks" className="w3-container">
            <div className="image-preview">
              <img src="/images/test_image.png" alt="Image 1" />
              <br />
            </div>
            <div className="image-preview">
              <img src="/images/test_image1.png" alt="Image 2" />
              <br />
            </div>
          </div>
        )}

        {/* Main Form */}
        <form className="w3-container w3-margin" onSubmit={handleHideMessage}>
          {/* File Type Selection */}
          <label className="w3-text-teal">
            <b>Select Input Type</b>
          </label>
          <select
            className="w3-select w3-border"
            value={filetype}
            onChange={handleFiletypeChange}
          >
            <option value="image">Image</option>
            <option value="audio">Audio (WAV)</option>
          </select>
          <br />
          <br />

          {/* Image Upload */}
          {filetype === 'image' && (
            <div className="upload-section">
              <div className="w3-cell">
                <input
                  ref={fileInputRef1}
                  className="w3-btn w3-blue-grey"
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                />
                <br />
                <br />
              </div>
              <div className="w3-cell">
                <input
                  ref={fileInputRef2}
                  className="w3-btn w3-blue-grey"
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                />
                <br />
                <br />
              </div>
            </div>
          )}

          {/* Audio Upload */}
          {filetype === 'audio' && (
            <div className="upload-section">
              <input
                ref={audioInputRef}
                className="w3-btn w3-blue-grey"
                type="file"
                accept=".wav"
                onChange={handleAudioUpload}
              />
              <br />
              <br />
            </div>
          )}

          {/* Message Input */}
          <label className="w3-text-teal">
            <b>Secret Message</b>
          </label>
          <textarea
            className="w3-input w3-border w3-light-grey"
            rows="10"
            cols="47"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type Your Message Here..!!"
          ></textarea>
          <br />

          {/* Hide Button */}
          <button className="w3-btn w3-blue-grey" type="submit" disabled={loading}>
            {loading ? 'Processing...' : 'Hide'}
          </button>

          {/* Messages */}
          {error && <p style={{ color: '#d32f2f', marginTop: '10px' }}><strong>Error:</strong> {error}</p>}
          {success && <p style={{ color: '#388e3c', marginTop: '10px' }}><strong>Success:</strong> {success}</p>}
        </form>

        <br />
        <footer className="w3-container w3-blue">
          <h5></h5>
        </footer>
      </div>

      {/* Cipher Text Card */}
      {cipher && (
        <div className="w3-card-4 w3-margin">
          <header className="w3-container w3-blue">
            <h1>Cipher Text</h1>
          </header>
          <div 
            style={{
              backgroundColor: '#f5f5f5',
              padding: '15px',
              borderRadius: '4px',
              maxHeight: '300px',
              overflowY: 'auto',
              border: '1px solid #ddd',
              wordBreak: 'break-all',
              fontFamily: "'Courier New', monospace",
              fontSize: '14px',
              lineHeight: '1.5'
            }}
          >
            <p style={{ margin: 0, color: '#000000' }}>{cipher}</p>
          </div>
          <footer className="w3-container w3-blue">
            <h5></h5>
          </footer>
        </div>
      )}

      {/* Stego Image Card */}
      {filetype === 'image' && (
        <div className="w3-card-4 w3-margin">
          <header className="w3-container w3-blue">
            <h1>Stego-Image</h1>
          </header>
          <div className="w3-cell">
            <img src="/images/stegoImage.png" alt="Stego" style={{ width: '100%' }} />
            <br />
          </div>
          <footer className="w3-container w3-blue">
            <h5></h5>
          </footer>
        </div>
      )}

      {/* Audio List Card */}
      <div className="w3-card-4 w3-margin">
        <header className="w3-container w3-blue">
          <h1>Uploaded Audio Files with Encrypted Messages</h1>
        </header>
        <div className="w3-container">
          {audioListLoading ? (
            <p>Loading audio files...</p>
          ) : audioList.length === 0 ? (
            <p style={{ color: '#666', margin: '15px 0' }}>No audio files uploaded yet.</p>
          ) : (
            <table className="w3-table w3-striped w3-border" style={{ marginTop: '15px' }}>
              <thead>
                <tr className="w3-blue">
                  <th>Audio File</th>
                  <th>Encrypted Message (Cipher Text)</th>
                  <th>Uploaded Time</th>
                </tr>
              </thead>
              <tbody>
                {audioList.map((audio, index) => (
                  <tr key={index}>
                    <td style={{ wordBreak: 'break-word', maxWidth: '150px' }}>
                      <strong>{audio.filename}</strong>
                    </td>
                    <td style={{ wordBreak: 'break-all', maxWidth: '300px', fontSize: '12px', fontFamily: "'Courier New', monospace", color: '#007cff' }}>
                      {audio.cipher_text.substring(0, 80)}{audio.cipher_text.length > 80 ? '...' : ''}
                    </td>
                    <td style={{ fontSize: '12px' }}>
                      {audio.timestamp}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
        <footer className="w3-container w3-blue">
          <h5></h5>
        </footer>
      </div>
    </div>
  );
}

export default Encryption;
