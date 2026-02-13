import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { authService } from '../services/apiService';
import '../css/w3.css';
import './Layout.css';

function Layout({ children }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [user, setUser] = useState(null);

  useEffect(() => {
    const currentUser = authService.getCurrentUser();
    setUser(currentUser);
  }, [location]);

  const handleLogout = async () => {
    try {
      await authService.logout();
      setUser(null);
      navigate('/');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const isLoginPage = location.pathname === '/';

  return (
    <div className="layout-container">
      {/* Sidebar Navigation */}
      {!isLoginPage && (
        <div className="w3-sidebar w3-light-grey w3-bar-block sidebar">
          <h3 className="w3-bar-item">Menu</h3>
          <a 
            href="/home" 
            className="w3-bar-item w3-button"
            onClick={() => navigate('/home')}
          >
            Home
          </a>
          <a 
            href="/info" 
            className="w3-bar-item w3-button"
            onClick={() => navigate('/info')}
          >
            About
          </a>
          <a 
            href="/encryption" 
            className="w3-bar-item w3-button"
            onClick={() => navigate('/encryption')}
          >
            Encryption
          </a>
          <a 
            href="/decryption" 
            className="w3-bar-item w3-button"
            onClick={() => navigate('/decryption')}
          >
            Decryption
          </a>
          <a 
            href="/face-enrollment" 
            className="w3-bar-item w3-button"
            onClick={() => navigate('/face-enrollment')}
            style={{ backgroundColor: '#ff9800', color: 'white' }}
          >
            👤 Face Enrollment
          </a>

          {user && (
            <a 
              className="w3-bar-item w3-button"
              onClick={handleLogout}
              style={{ cursor: 'pointer', color: '#d32f2f' }}
            >
              Logout ({user})
            </a>
          )}
        </div>
      )}

      {/* Page Content */}
      <div className={isLoginPage ? 'full-width' : 'page-content'}>
        <div className="w3-container w3-teal header">
          <h1>Secure communication using multi-image steganography and face recognition</h1>
        </div>

        {children}

        {/* Footer */}
        {!isLoginPage && (
          <div className="w3-container w3-teal footer">
            <div className="w3-container w3-cell w3-mobile" style={{ width: '85%' }}>
              <h5></h5>
              <div className="w3-container w3-cell">
                <p></p>
                <p></p>
              </div>
              <div className="w3-container w3-cell">
                <p></p>
                <p></p>
              </div>
            </div>
            <div className="w3-container w3-cell w3-mobile">
              <h5></h5>
              <p></p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Layout;
