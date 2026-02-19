import React, { useState } from 'react'
import toast from 'react-hot-toast'
import api from '../utils/api.js'

export default function EncodePage() {
  const [image, setImage] = useState(null)
  const [preview, setPreview] = useState(null)
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [downloadUrl, setDownloadUrl] = useState(null)

  function handleImageChange(e) {
    const file = e.target.files[0]
    if (!file) return
    setImage(file)
    setDownloadUrl(null)
    setPreview(URL.createObjectURL(file))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!image) { toast.error('Please select an image'); return }
    if (!message.trim()) { toast.error('Please enter a secret message'); return }

    setLoading(true)
    const formData = new FormData()
    formData.append('image', image)
    formData.append('message', message)

    try {
      const { data } = await api.post('/stego/encode', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setDownloadUrl(data.downloadUrl)
      toast.success('Message encoded successfully!')
    } catch (err) {
      toast.error(err.response?.data?.error || 'Encoding failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <span className="text-4xl">🔒</span> Encode Message
        </h1>
        <p className="mt-2 text-gray-400">
          Hide your AES-encrypted secret inside an image using LSB steganography.
        </p>
      </div>

      <div className="bg-gray-800 border border-gray-700 rounded-2xl p-8 shadow-xl">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">
              Carrier Image
            </label>
            <div className="border-2 border-dashed border-gray-600 rounded-xl p-6 text-center hover:border-indigo-500 transition-colors">
              <input
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                className="hidden"
                id="encode-image"
              />
              <label htmlFor="encode-image" className="cursor-pointer">
                {preview ? (
                  <img
                    src={preview}
                    alt="Preview"
                    className="max-h-48 mx-auto rounded-lg object-contain"
                  />
                ) : (
                  <div className="text-gray-500">
                    <p className="text-4xl mb-2">🖼️</p>
                    <p className="text-sm">Click to select image (PNG/JPG)</p>
                  </div>
                )}
              </label>
            </div>
            {image && (
              <p className="mt-1.5 text-xs text-gray-500">{image.name}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">
              Secret Message
            </label>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              rows={4}
              placeholder="Enter your secret message here…"
              className="w-full bg-gray-700 border border-gray-600 text-white placeholder-gray-500 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition resize-none"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-lg transition-colors"
          >
            {loading ? 'Encoding…' : 'Encode & Download'}
          </button>
        </form>

        {downloadUrl && (
          <div className="mt-6 p-4 bg-green-900/30 border border-green-700 rounded-xl">
            <p className="text-green-400 font-medium mb-3">✅ Stego image ready!</p>
            <a
              href={downloadUrl}
              download
              className="inline-flex items-center gap-2 bg-green-700 hover:bg-green-600 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
            >
              ⬇️ Download Stego Image
            </a>
          </div>
        )}
      </div>
    </div>
  )
}
