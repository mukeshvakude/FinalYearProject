import React from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  if (!user) return null

  function handleLogout() {
    logout()
    navigate('/login')
  }

  const linkClass = (path) =>
    `text-sm font-medium transition-colors hover:text-indigo-400 ${
      location.pathname === path ? 'text-indigo-400' : 'text-gray-300'
    }`

  return (
    <nav className="bg-gray-800 border-b border-gray-700 px-6 py-4">
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        <Link to="/dashboard" className="flex items-center gap-2">
          <span className="text-2xl">🔐</span>
          <span className="text-xl font-bold text-white">SecureVision</span>
          <span className="text-indigo-400 font-semibold text-sm">Stego</span>
        </Link>

        <div className="flex items-center gap-6">
          <Link to="/dashboard" className={linkClass('/dashboard')}>Dashboard</Link>
          <Link to="/encode" className={linkClass('/encode')}>Encode</Link>
          <Link to="/decode" className={linkClass('/decode')}>Decode</Link>
          <Link to="/face" className={linkClass('/face')}>Face Verify</Link>

          <div className="flex items-center gap-3 border-l border-gray-600 pl-6">
            <span className="text-sm text-gray-400">
              Hi, <span className="text-white font-medium">{user.username}</span>
            </span>
            <button
              onClick={handleLogout}
              className="text-sm bg-red-600 hover:bg-red-700 text-white px-3 py-1.5 rounded-lg transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}
