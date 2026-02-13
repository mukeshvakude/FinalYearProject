import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Login from './components/Login';
import Home from './components/Home';
import Info from './components/Info';
import Encryption from './components/Encryption';
import Decryption from './components/Decryption';
import FaceEnrollmentPage from './components/FaceEnrollmentPage';
import PrivateRoute from './components/PrivateRoute';
import './css/w3.css';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        {/* Login Route */}
        <Route
          path="/"
          element={
            <Layout>
              <Login />
            </Layout>
          }
        />

        {/* Protected Routes */}
        <Route
          path="/home"
          element={
            <Layout>
              <PrivateRoute>
                <Home />
              </PrivateRoute>
            </Layout>
          }
        />

        <Route
          path="/info"
          element={
            <Layout>
              <PrivateRoute>
                <Info />
              </PrivateRoute>
            </Layout>
          }
        />

        <Route
          path="/encryption"
          element={
            <Layout>
              <PrivateRoute>
                <Encryption />
              </PrivateRoute>
            </Layout>
          }
        />

        <Route
          path="/decryption"
          element={
            <Layout>
              <PrivateRoute>
                <Decryption />
              </PrivateRoute>
            </Layout>
          }
        />

        <Route
          path="/face-enrollment"
          element={
            <Layout>
              <PrivateRoute>
                <FaceEnrollmentPage />
              </PrivateRoute>
            </Layout>
          }
        />

        {/* Catch-all route */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

export default App;
