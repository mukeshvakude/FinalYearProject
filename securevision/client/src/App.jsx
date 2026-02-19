import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from './context/AuthContext.jsx'
import Navbar from './components/Navbar.jsx'
import LoginPage from './pages/LoginPage.jsx'
import RegisterPage from './pages/RegisterPage.jsx'
import DashboardPage from './pages/DashboardPage.jsx'
import EncodePage from './pages/EncodePage.jsx'
import DecodePage from './pages/DecodePage.jsx'
import FaceVerifyPage from './pages/FaceVerifyPage.jsx'

function ProtectedRoute({ children }) {
  const token = localStorage.getItem('token')
  if (!token) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-gray-900 text-white">
          <Navbar />
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/encode"
              element={
                <ProtectedRoute>
                  <EncodePage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/decode"
              element={
                <ProtectedRoute>
                  <DecodePage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/face"
              element={
                <ProtectedRoute>
                  <FaceVerifyPage />
                </ProtectedRoute>
              }
            />
          </Routes>
        </div>
        <Toaster
          position="top-right"
          toastOptions={{
            style: { background: '#1f2937', color: '#f9fafb', border: '1px solid #374151' }
          }}
        />
      </BrowserRouter>
    </AuthProvider>
  )
}
