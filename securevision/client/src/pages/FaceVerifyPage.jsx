import React, { useState } from 'react'
import toast from 'react-hot-toast'
import api from '../utils/api.js'

function ImageUpload({ id, label, onChange, preview }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-300 mb-1.5">{label}</label>
      <div className="border-2 border-dashed border-gray-600 rounded-xl p-4 text-center hover:border-indigo-500 transition-colors">
        <input
          type="file"
          accept="image/*"
          onChange={onChange}
          className="hidden"
          id={id}
        />
        <label htmlFor={id} className="cursor-pointer block">
          {preview ? (
            <img src={preview} alt="Preview" className="max-h-36 mx-auto rounded-lg object-contain" />
          ) : (
            <div className="text-gray-500 py-4">
              <p className="text-3xl mb-1">👤</p>
              <p className="text-xs">Click to upload face image</p>
            </div>
          )}
        </label>
      </div>
    </div>
  )
}

export default function FaceVerifyPage() {
  const [image1, setImage1] = useState(null)
  const [image2, setImage2] = useState(null)
  const [preview1, setPreview1] = useState(null)
  const [preview2, setPreview2] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  function handleImg1(e) {
    const f = e.target.files[0]
    if (!f) return
    setImage1(f)
    setPreview1(URL.createObjectURL(f))
    setResult(null)
  }

  function handleImg2(e) {
    const f = e.target.files[0]
    if (!f) return
    setImage2(f)
    setPreview2(URL.createObjectURL(f))
    setResult(null)
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!image1 || !image2) { toast.error('Please upload both face images'); return }

    setLoading(true)
    const formData = new FormData()
    formData.append('image1', image1)
    formData.append('image2', image2)

    try {
      const { data } = await api.post('/face/verify', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setResult(data)
      toast.success('Verification complete!')
    } catch (err) {
      toast.error(err.response?.data?.error || 'Face verification failed')
    } finally {
      setLoading(false)
    }
  }

  const verified = result?.verified

  return (
    <div className="max-w-2xl mx-auto px-4 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <span className="text-4xl">👤</span> Face Verification
        </h1>
        <p className="mt-2 text-gray-400">
          Upload two face images and our AI will determine if they belong to the same person.
        </p>
      </div>

      <div className="bg-gray-800 border border-gray-700 rounded-2xl p-8 shadow-xl">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <ImageUpload id="face1" label="Face Image 1" onChange={handleImg1} preview={preview1} />
            <ImageUpload id="face2" label="Face Image 2" onChange={handleImg2} preview={preview2} />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-lg transition-colors"
          >
            {loading ? 'Analyzing…' : 'Verify Faces'}
          </button>
        </form>

        {result && (
          <div
            className={`mt-6 p-5 border rounded-xl ${
              verified
                ? 'bg-green-900/30 border-green-700'
                : 'bg-red-900/30 border-red-700'
            }`}
          >
            <div className="flex items-center gap-3 mb-4">
              <span className="text-3xl">{verified ? '✅' : '❌'}</span>
              <div>
                <p className={`text-lg font-bold ${verified ? 'text-green-400' : 'text-red-400'}`}>
                  {verified ? 'Same Person' : 'Different People'}
                </p>
                <p className="text-sm text-gray-400">
                  {verified ? 'The faces match.' : 'The faces do not match.'}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3 text-center">
              <div className="bg-gray-900/50 rounded-lg p-3">
                <p className="text-2xl font-bold text-white">
                  {result.similarity_score != null ? `${result.similarity_score}%` : '—'}
                </p>
                <p className="text-xs text-gray-400 mt-1">Similarity</p>
              </div>
              <div className="bg-gray-900/50 rounded-lg p-3">
                <p className="text-2xl font-bold text-white">
                  {result.distance != null ? result.distance.toFixed(4) : '—'}
                </p>
                <p className="text-xs text-gray-400 mt-1">Distance</p>
              </div>
              <div className="bg-gray-900/50 rounded-lg p-3">
                <p className="text-2xl font-bold text-white">
                  {result.threshold != null ? result.threshold.toFixed(4) : '—'}
                </p>
                <p className="text-xs text-gray-400 mt-1">Threshold</p>
              </div>
            </div>

            {result.model && (
              <p className="mt-3 text-xs text-gray-500 text-right">
                Model: {result.model}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
