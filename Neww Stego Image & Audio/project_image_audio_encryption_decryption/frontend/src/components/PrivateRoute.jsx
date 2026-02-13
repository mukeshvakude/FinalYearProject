import React from 'react';
import { Navigate } from 'react-router-dom';
import { authService } from '../services/apiService';

function PrivateRoute({ children }) {
  const isAuthenticated = authService.isAuthenticated();

  if (!isAuthenticated) {
    return <Navigate to="/" />;
  }

  return children;
}

export default PrivateRoute;
