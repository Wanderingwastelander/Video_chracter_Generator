import { useState, useEffect } from 'react'
import { getEnvironments, createEnvironment, deleteEnvironment } from '../services/api'

function Environments() {
  const [environments, setEnvironments] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [newEnv, setNewEnv] = useState({ name: '', description: '' })
  
  useEffect(() => {
    loadEnvironments()
  }, [])
  
  const loadEnvironments = async () => {
    try {
      const res = await getEnvironments()
      setEnvironments(res.data)
    } catch (error) {
      console.error('Failed to load environments:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const handleCreate = async (e) => {
    e.preventDefault()
    
    try {
      const formData = new FormData()
      formData.append('name', newEnv.name)
      if (newEnv.description) {
        formData.append('description', newEnv.description)
      }
      
      await createEnvironment(formData)
      setShowCreate(false)
      setNewEnv({ name: '', description: '' })
      loadEnvironments()
    } catch (error) {
      console.error('Failed to create environment:', error)
      alert('Failed to create environment')
    }
  }
  
  const handleDelete = async (id, name) => {
    if (!confirm(`Delete environment "${name}"?`)) return
    
    try {
      await deleteEnvironment(id)
      setEnvironments(environments.filter(e => e.id !== id))
    } catch (error) {
      console.error('Failed to delete environment:', error)
      alert('Failed to delete environment')
    }
  }
  
  if (loading) {
    return <div className="text-gray-400">Loading...</div>
  }
  
  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Environments</h1>
        <button
          onClick={() => setShowCreate(true)}
          className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded-lg font-medium transition-colors"
        >
          + New Environment
        </button>
      </div>
      
      {/* Create Modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">New Environment</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Name</label>
                <input
                  type="text"
                  value={newEnv.name}
                  onChange={(e) => setNewEnv({...newEnv, name: e.target.value})}
                  required
                  className="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2"
                  placeholder="e.g. Tavern Interior"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Description</label>
                <textarea
                  value={newEnv.description}
                  onChange={(e) => setNewEnv({...newEnv, description: e.target.value})}
                  rows={3}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2"
                  placeholder="Describe the environment..."
                />
              </div>
              <div className="flex gap-4">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 hover:bg-blue-700 py-2 rounded font-medium"
                >
                  Create
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreate(false)}
                  className="flex-1 bg-gray-700 hover:bg-gray-600 py-2 rounded font-medium"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      {/* Environment List */}
      {environments.length === 0 ? (
        <div className="bg-gray-800 rounded-lg p-8 text-center">
          <p className="text-gray-400 mb-4">No environments yet</p>
          <button
            onClick={() => setShowCreate(true)}
            className="text-blue-400 hover:underline"
          >
            Create your first environment →
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {environments.map(env => (
            <div key={env.id} className="bg-gray-800 rounded-lg overflow-hidden">
              <div className="h-40 bg-gray-700 flex items-center justify-center">
                <span className="text-4xl">🏠</span>
              </div>
              
              <div className="p-4">
                <h3 className="text-xl font-bold mb-2">{env.name}</h3>
                {env.description && (
                  <p className="text-sm text-gray-400 mb-4">{env.description}</p>
                )}
                <p className="text-xs text-gray-500 mb-4">
                  {env.id}
                </p>
                
                <div className="flex gap-2">
                  <button className="flex-1 bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded transition-colors">
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(env.id, env.name)}
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

export default Environments
