import React, { useState } from 'react'
import toast from 'react-hot-toast'
import api from '../utils/api.js'

export default function DecodePage() {
  const [image, setImage] = useState(null)
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  function handleImageChange(e) {
    const file = e.target.files[0]
    if (!file) return
    setImage(file)
    setResult(null)
    setPreview(URL.createObjectURL(file))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!image) { toast.error('Please select a stego image'); return }

    setLoading(true)
    const formData = new FormData()
    formData.append('image', image)

    try {
      const { data } = await api.post('/stego/decode', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setResult(data.message)
      toast.success('Message extracted!')
    } catch (err) {
      toast.error(err.response?.data?.error || 'Decoding failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <span className="text-4xl">🔓</span> Decode Message
        </h1>
        <p className="mt-2 text-gray-400">
          Upload a stego image to extract and decrypt the hidden message.
        </p>
      </div>

      <div className="bg-gray-800 border border-gray-700 rounded-2xl p-8 shadow-xl">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">
              Stego Image
            </label>
            <div className="border-2 border-dashed border-gray-600 rounded-xl p-6 text-center hover:border-indigo-500 transition-colors">
              <input
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                className="hidden"
                id="decode-image"
              />
              <label htmlFor="decode-image" className="cursor-pointer">
                {preview ? (
                  <img
                    src={preview}
                    alt="Preview"
                    className="max-h-48 mx-auto rounded-lg object-contain"
                  />
                ) : (
                  <div className="text-gray-500">
                    <p className="text-4xl mb-2">🖼️</p>
                    <p className="text-sm">Click to select stego image</p>
                  </div>
                )}
              </label>
            </div>
            {image && (
              <p className="mt-1.5 text-xs text-gray-500">{image.name}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-lg transition-colors"
          >
            {loading ? 'Decoding…' : 'Extract Message'}
          </button>
        </form>

        {result !== null && (
          <div className="mt-6 p-5 bg-indigo-900/30 border border-indigo-700 rounded-xl">
            <p className="text-indigo-400 font-medium mb-2">💬 Extracted Message</p>
            <p className="text-white text-sm bg-gray-900/60 rounded-lg p-3 break-words whitespace-pre-wrap font-mono">
              {result}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
