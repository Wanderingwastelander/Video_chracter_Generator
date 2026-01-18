import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { createCharacter } from '../services/api'

function CreateCharacter() {
  const navigate = useNavigate()
  const [sourceType, setSourceType] = useState('dndbeyond')
  const [formData, setFormData] = useState({
    name: '',
    sourceUrl: '',
    description: '',
    sex: '',
    height: ''
  })
  const [referenceImage, setReferenceImage] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)
  
  const handleImageChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setReferenceImage(file)
      const reader = new FileReader()
      reader.onload = (e) => setImagePreview(e.target.result)
      reader.readAsDataURL(file)
    }
  }
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setSubmitting(true)
    
    try {
      const data = new FormData()
      data.append('source_type', sourceType)
      
      if (sourceType === 'dndbeyond') {
        data.append('source_url', formData.sourceUrl)
      }
      
      if (formData.name) data.append('name', formData.name)
      if (formData.description) data.append('description', formData.description)
      if (formData.sex) data.append('sex', formData.sex)
      if (formData.height) data.append('height', formData.height)
      
      if (referenceImage) {
        data.append('reference_image', referenceImage)
      }
      
      const res = await createCharacter(data)
      navigate(`/characters/${res.data.id}`)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to create character')
    } finally {
      setSubmitting(false)
    }
  }
  
  return (
    <div className="max-w-2xl">
      <Link to="/characters" className="text-blue-400 hover:underline mb-4 block">
        ← Back to Characters
      </Link>
      
      <h1 className="text-3xl font-bold mb-8">New Character</h1>
      
      {error && (
        <div className="bg-red-900 border border-red-700 text-red-200 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Source Type */}
        <div>
          <label className="block text-sm font-medium mb-2">Source Type</label>
          <div className="flex gap-4">
            {[
              { value: 'dndbeyond', label: 'D&D Beyond' },
              { value: 'manual', label: 'Manual Entry' },
              { value: 'description', label: 'From Description' }
            ].map(opt => (
              <label key={opt.value} className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="sourceType"
                  value={opt.value}
                  checked={sourceType === opt.value}
                  onChange={(e) => setSourceType(e.target.value)}
                  className="text-blue-600"
                />
                {opt.label}
              </label>
            ))}
          </div>
        </div>
        
        {/* D&D Beyond URL */}
        {sourceType === 'dndbeyond' && (
          <div>
            <label className="block text-sm font-medium mb-2">D&D Beyond URL</label>
            <input
              type="url"
              value={formData.sourceUrl}
              onChange={(e) => setFormData({...formData, sourceUrl: e.target.value})}
              placeholder="https://www.dndbeyond.com/characters/123456789"
              className="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2"
            />
            <p className="text-sm text-gray-500 mt-1">
              Paste your character's D&D Beyond URL
            </p>
          </div>
        )}
        
        {/* Character Name */}
        <div>
          <label className="block text-sm font-medium mb-2">
            Character Name {sourceType === 'dndbeyond' && '(optional - will be fetched)'}
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
            placeholder="Enter character name"
            className="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2"
            required={sourceType !== 'dndbeyond'}
          />
        </div>
        
        {/* Manual/Description fields */}
        {sourceType !== 'dndbeyond' && (
          <>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Sex</label>
                <select
                  value={formData.sex}
                  onChange={(e) => setFormData({...formData, sex: e.target.value})}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2"
                >
                  <option value="">Select...</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Height</label>
                <input
                  type="text"
                  value={formData.height}
                  onChange={(e) => setFormData({...formData, height: e.target.value})}
                  placeholder="e.g. 5'10&quot; or 178cm"
                  className="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2"
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                placeholder="Describe the character's appearance (build, features, etc.)"
                rows={4}
                className="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2"
              />
              <p className="text-sm text-gray-500 mt-1">
                Include details like body type (muscular, lean, stocky), distinguishing features, etc.
              </p>
            </div>
          </>
        )}
        
        {/* Reference Image */}
        <div>
          <label className="block text-sm font-medium mb-2">Reference Image</label>
          <div className="flex gap-4 items-start">
            <div className="flex-1">
              <input
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                className="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-gray-600 file:text-white"
              />
              <p className="text-sm text-gray-500 mt-1">
                Upload a reference image for the character. This will be used to generate consistent assets.
              </p>
            </div>
            
            {imagePreview && (
              <div className="w-32 h-32 bg-gray-700 rounded overflow-hidden flex-shrink-0">
                <img src={imagePreview} alt="Preview" className="w-full h-full object-cover" />
              </div>
            )}
          </div>
        </div>
        
        {/* Submit */}
        <div className="flex gap-4 pt-4">
          <button
            type="submit"
            disabled={submitting}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 px-8 py-3 rounded-lg font-medium transition-colors"
          >
            {submitting ? 'Creating...' : 'Create Character'}
          </button>
          
          <Link
            to="/characters"
            className="bg-gray-700 hover:bg-gray-600 px-8 py-3 rounded-lg font-medium transition-colors"
          >
            Cancel
          </Link>
        </div>
      </form>
    </div>
  )
}

export default CreateCharacter
