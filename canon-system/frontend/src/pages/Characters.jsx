import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getCharacters, deleteCharacter } from '../services/api'

function Characters() {
  const [characters, setCharacters] = useState([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    loadCharacters()
  }, [])
  
  const loadCharacters = async () => {
    try {
      const res = await getCharacters()
      setCharacters(res.data)
    } catch (error) {
      console.error('Failed to load characters:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const handleDelete = async (id, name) => {
    if (!confirm(`Delete character "${name}"? This cannot be undone.`)) {
      return
    }
    
    try {
      await deleteCharacter(id)
      setCharacters(characters.filter(c => c.id !== id))
    } catch (error) {
      console.error('Failed to delete character:', error)
      alert('Failed to delete character')
    }
  }
  
  const getStatusColor = (status) => {
    switch (status) {
      case 'approved': return 'text-green-400'
      case 'generating': return 'text-blue-400'
      case 'review': return 'text-yellow-400'
      case 'pending': return 'text-gray-400'
      default: return 'text-gray-400'
    }
  }
  
  if (loading) {
    return <div className="text-gray-400">Loading...</div>
  }
  
  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Characters</h1>
        <Link
          to="/characters/new"
          className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded-lg font-medium transition-colors"
        >
          + New Character
        </Link>
      </div>
      
      {characters.length === 0 ? (
        <div className="bg-gray-800 rounded-lg p-8 text-center">
          <p className="text-gray-400 mb-4">No characters yet</p>
          <Link
            to="/characters/new"
            className="text-blue-400 hover:underline"
          >
            Create your first character →
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {characters.map(char => (
            <div key={char.id} className="bg-gray-800 rounded-lg overflow-hidden">
              {/* Thumbnail */}
              <div className="h-48 bg-gray-700 flex items-center justify-center">
                {char.reference_image_path ? (
                  <img
                    src={`/files/characters/${char.id}/reference_image.png`}
                    alt={char.name}
                    className="h-full w-full object-cover"
                    onError={(e) => {
                      e.target.style.display = 'none'
                    }}
                  />
                ) : (
                  <span className="text-6xl text-gray-600">👤</span>
                )}
              </div>
              
              {/* Info */}
              <div className="p-4">
                <h3 className="text-xl font-bold mb-2">{char.name}</h3>
                
                <div className="text-sm text-gray-400 space-y-1 mb-4">
                  <p>
                    <span className="text-gray-500">Layers:</span>{' '}
                    {char.sex} / {char.skeleton} / {char.body_composition} / {char.species}
                  </p>
                  <p>
                    <span className="text-gray-500">Status:</span>{' '}
                    <span className={getStatusColor(char.status)}>{char.status}</span>
                  </p>
                  {char.source_type && (
                    <p>
                      <span className="text-gray-500">Source:</span> {char.source_type}
                    </p>
                  )}
                </div>
                
                <div className="flex gap-2">
                  <Link
                    to={`/characters/${char.id}`}
                    className="flex-1 bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded text-center transition-colors"
                  >
                    View
                  </Link>
                  <button
                    onClick={() => handleDelete(char.id, char.name)}
                    className="px-4 py-2 rounded bg-red-900 hover:bg-red-800 transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Characters
