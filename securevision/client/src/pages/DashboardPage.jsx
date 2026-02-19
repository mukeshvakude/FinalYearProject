import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

const features = [
  {
    to: '/encode',
    icon: '🔒',
    title: 'Encode Message',
    desc: 'Hide an AES-encrypted secret inside any image using LSB steganography.',
    color: 'from-indigo-600 to-indigo-800'
  },
  {
    to: '/decode',
    icon: '🔓',
    title: 'Decode Message',
    desc: 'Extract and decrypt a hidden message from a stego image.',
    color: 'from-purple-600 to-purple-800'
  },
  {
    to: '/face',
    icon: '👤',
    title: 'Face Verification',
    desc: 'Compare two face images using DeepFace AI to check if they match.',
    color: 'from-teal-600 to-teal-800'
  }
]

export default function DashboardPage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-12">
      <div className="mb-10">
        <h1 className="text-4xl font-bold text-white">
          Welcome back, <span className="text-indigo-400">{user?.username}</span> 👋
        </h1>
        <p className="mt-2 text-gray-400 text-lg">
          Choose a feature below to get started.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        {features.map((f) => (
          <Link
            key={f.to}
            to={f.to}
            className="group bg-gray-800 border border-gray-700 rounded-2xl p-6 hover:border-indigo-500 transition-all hover:shadow-lg hover:shadow-indigo-900/30"
          >
            <div
              className={`w-12 h-12 rounded-xl bg-gradient-to-br ${f.color} flex items-center justify-center text-2xl mb-4 group-hover:scale-110 transition-transform`}
            >
              {f.icon}
            </div>
            <h2 className="text-xl font-semibold text-white mb-2">{f.title}</h2>
            <p className="text-gray-400 text-sm leading-relaxed">{f.desc}</p>
            <div className="mt-4 flex items-center text-indigo-400 text-sm font-medium">
              Get started <span className="ml-1 group-hover:translate-x-1 transition-transform">→</span>
            </div>
          </Link>
        ))}
      </div>

      <div className="bg-gray-800 border border-gray-700 rounded-2xl p-6">
        <h3 className="text-lg font-semibold text-white mb-2">Account Info</h3>
        <div className="flex flex-wrap gap-4 text-sm text-gray-400">
          <span>👤 Username: <span className="text-white">{user?.username}</span></span>
          <span>✉️ Email: <span className="text-white">{user?.email}</span></span>
        </div>
        <button
          onClick={handleLogout}
          className="mt-4 text-sm text-red-400 hover:text-red-300 transition-colors"
        >
          Sign out →
        </button>
      </div>
    </div>
  )
}
