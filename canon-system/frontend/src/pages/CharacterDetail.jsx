import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getCharacter, generateCharacterAssets, getGenerators } from '../services/api'

function CharacterDetail() {
  const { id } = useParams()
  const [character, setCharacter] = useState(null)
  const [generators, setGenerators] = useState([])
  const [selectedGenerator, setSelectedGenerator] = useState('mock')
  const [generating, setGenerating] = useState(false)
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    loadCharacter()
    loadGenerators()
  }, [id])
  
  const loadCharacter = async () => {
    try {
      const res = await getCharacter(id)
      setCharacter(res.data)
    } catch (error) {
      console.error('Failed to load character:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const loadGenerators = async () => {
    try {
      const res = await getGenerators()
      setGenerators(res.data.available)
      setSelectedGenerator(res.data.default)
    } catch (error) {
      console.error('Failed to load generators:', error)
    }
  }
  
  const handleGenerate = async () => {
    if (!confirm('Generate all face and body assets? This will queue generation jobs.')) {
      return
    }
    
    setGenerating(true)
    try {
      const res = await generateCharacterAssets(id, {
        generate_faces: true,
        generate_body: true,
        generator: selectedGenerator
      })
      alert(`Queued ${res.data.jobs_queued} generation jobs. Check the Approval Queue for results.`)
      loadCharacter()
    } catch (error) {
      console.error('Failed to generate:', error)
      alert('Failed to start generation: ' + (error.response?.data?.detail || error.message))
    } finally {
      setGenerating(false)
    }
  }
  
  if (loading) {
    return <div className="text-gray-400">Loading...</div>
  }
  
  if (!character) {
    return <div className="text-red-400">Character not found</div>
  }
  
  const faceAssets = character.assets?.filter(a => a.asset_type === 'face') || []
  const bodyAssets = character.assets?.filter(a => a.asset_type === 'body') || []
  
  const getStatusBadge = (status) => {
    const colors = {
      approved: 'bg-green-900 text-green-300',
      generating: 'bg-blue-900 text-blue-300',
      review: 'bg-yellow-900 text-yellow-300',
      rejected: 'bg-red-900 text-red-300',
      pending: 'bg-gray-700 text-gray-300'
    }
    return colors[status] || colors.pending
  }
  
  return (
    <div>
      <div className="flex justify-between items-start mb-8">
        <div>
          <Link to="/characters" className="text-blue-400 hover:underline mb-2 block">
            ← Back to Characters
          </Link>
          <h1 className="text-3xl font-bold">{character.name}</h1>
          <span className={`inline-block px-3 py-1 rounded-full text-sm mt-2 ${getStatusBadge(character.status)}`}>
            {character.status}
          </span>
        </div>
        
        <div className="flex items-center gap-4">
          <select
            value={selectedGenerator}
            onChange={(e) => setSelectedGenerator(e.target.value)}
            className="bg-gray-700 border border-gray-600 rounded px-4 py-2"
          >
            {generators.map(g => (
              <option key={g} value={g}>{g}</option>
            ))}
          </select>
          
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 px-6 py-2 rounded-lg font-medium transition-colors"
          >
            {generating ? 'Generating...' : 'Generate Assets'}
          </button>
        </div>
      </div>
      
      {/* Character Info */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        {/* Reference Image */}
        <div className="bg-gray-800 rounded-lg p-4">
          <h3 className="text-lg font-bold mb-4">Reference Image</h3>
          <div className="aspect-square bg-gray-700 rounded flex items-center justify-center">
            {character.reference_image_path ? (
              <img
                src={`/files/characters/${character.id}/reference_image.png`}
                alt="Reference"
                className="max-h-full max-w-full object-contain"
              />
            ) : (
              <span className="text-gray-500">No reference image</span>
            )}
          </div>
        </div>
        
        {/* Canon Layers */}
        <div className="bg-gray-800 rounded-lg p-4">
          <h3 className="text-lg font-bold mb-4">Canon Layers</h3>
          <dl className="space-y-3">
            <div>
              <dt className="text-gray-500 text-sm">Sex</dt>
              <dd className="text-lg">{character.sex === 'M' ? 'Male' : 'Female'}</dd>
            </div>
            <div>
              <dt className="text-gray-500 text-sm">Skeleton</dt>
              <dd className="text-lg">{character.skeleton}</dd>
            </div>
            <div>
              <dt className="text-gray-500 text-sm">Body Composition</dt>
              <dd className="text-lg">{character.body_composition}</dd>
            </div>
            <div>
              <dt className="text-gray-500 text-sm">Species</dt>
              <dd className="text-lg">{character.species}</dd>
            </div>
          </dl>
        </div>
        
        {/* Source Info */}
        <div className="bg-gray-800 rounded-lg p-4">
          <h3 className="text-lg font-bold mb-4">Source</h3>
          <dl className="space-y-3">
            <div>
              <dt className="text-gray-500 text-sm">Type</dt>
              <dd className="text-lg">{character.source_type || 'Manual'}</dd>
            </div>
            {character.source_url && (
              <div>
                <dt className="text-gray-500 text-sm">URL</dt>
                <dd className="text-sm">
                  <a href={character.source_url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline break-all">
                    {character.source_url}
                  </a>
                </dd>
              </div>
            )}
            <div>
              <dt className="text-gray-500 text-sm">Created</dt>
              <dd>{new Date(character.created_at).toLocaleString()}</dd>
            </div>
          </dl>
        </div>
      </div>
      
      {/* Face Assets */}
      <div className="bg-gray-800 rounded-lg p-6 mb-8">
        <h3 className="text-xl font-bold mb-4">Face Canon</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {['NEUT', 'HPPY', 'SAD', 'ANGR', 'EYEC'].map(code => {
            const asset = faceAssets.find(a => a.asset_code === code)
            return (
              <div key={code} className="text-center">
                <div className="aspect-square bg-gray-700 rounded mb-2 flex items-center justify-center overflow-hidden">
                  {asset?.file_path ? (
                    <img
                      src={`/files/characters/${character.id}/face/${code}.png`}
                      alt={code}
                      className="max-h-full max-w-full object-contain"
                      onError={(e) => {
                        e.target.style.display = 'none'
                        e.target.nextSibling.style.display = 'block'
                      }}
                    />
                  ) : null}
                  <span className={`text-gray-500 ${asset?.file_path ? 'hidden' : ''}`}>
                    {asset ? '...' : '—'}
                  </span>
                </div>
                <p className="text-sm font-medium">{code}</p>
                {asset && (
                  <span className={`text-xs px-2 py-0.5 rounded ${getStatusBadge(asset.status)}`}>
                    {asset.status}
                  </span>
                )}
              </div>
            )
          })}
        </div>
      </div>
      
      {/* Body Assets */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-xl font-bold mb-4">Body Canon</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {['FRNT', 'Q34F', 'SIDE', 'Q34B', 'BACK'].map(code => {
            const asset = bodyAssets.find(a => a.asset_code === code)
            return (
              <div key={code} className="text-center">
                <div className="aspect-[3/4] bg-gray-700 rounded mb-2 flex items-center justify-center overflow-hidden">
                  {asset?.file_path ? (
                    <img
                      src={`/files/characters/${character.id}/body/${code}.png`}
                      alt={code}
                      className="max-h-full max-w-full object-contain"
                      onError={(e) => {
                        e.target.style.display = 'none'
                      }}
                    />
                  ) : null}
                  <span className={`text-gray-500 ${asset?.file_path ? 'hidden' : ''}`}>
                    {asset ? '...' : '—'}
                  </span>
                </div>
                <p className="text-sm font-medium">{code}</p>
                {asset && (
                  <span className={`text-xs px-2 py-0.5 rounded ${getStatusBadge(asset.status)}`}>
                    {asset.status}
                  </span>
                )}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default CharacterDetail
