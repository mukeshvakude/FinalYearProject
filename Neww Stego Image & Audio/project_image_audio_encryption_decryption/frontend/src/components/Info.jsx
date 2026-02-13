import React, { useEffect, useState } from 'react';
import { contentService } from '../services/apiService';
import '../css/w3.css';

function Info() {
  const [content, setContent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchContent = async () => {
      try {
        const data = await contentService.getInfo();
        setContent(data);
      } catch (err) {
        setError('Failed to load info content');
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

      {/* Abstract Card */}
      <div className="w3-card-4 w3-margin">
        <header className="w3-container w3-blue">
          <h1>{content?.abstract?.title}</h1>
        </header>
        <div className="w3-container">
          <p>{content?.abstract?.text}</p>
        </div>
        <footer className="w3-container w3-blue">
          <h5></h5>
        </footer>
      </div>

      {/* Motivation Card */}
      <div className="w3-card-4 w3-margin">
        <header className="w3-container w3-blue">
          <h1>{content?.motivation?.title}</h1>
        </header>
        <div className="w3-container">
          <p>{content?.motivation?.text}</p>
        </div>
        <footer className="w3-container w3-blue">
          <h5></h5>
        </footer>
      </div>
    </div>
  );
}

export default Info;
