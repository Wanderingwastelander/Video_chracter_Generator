import { useState, useEffect } from 'react'
import { getSyncStatus, initSync, pushChanges, pullChanges, getSyncLog, getGenerators } from '../services/api'

function Settings() {
  const [syncStatus, setSyncStatus] = useState(null)
  const [syncLog, setSyncLog] = useState([])
  const [generators, setGenerators] = useState([])
  const [repoUrl, setRepoUrl] = useState('')
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  
  useEffect(() => {
    loadSettings()
  }, [])
  
  const loadSettings = async () => {
    try {
      const [statusRes, logRes, genRes] = await Promise.all([
        getSyncStatus(),
        getSyncLog(10),
        getGenerators()
      ])
      
      setSyncStatus(statusRes.data)
      setSyncLog(logRes.data)
      setGenerators(genRes.data.available)
      setRepoUrl(statusRes.data.remote_url || '')
    } catch (error) {
      console.error('Failed to load settings:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const handleInitRepo = async () => {
    if (!repoUrl) {
      alert('Please enter a GitHub repository URL')
      return
    }
    
    setSyncing(true)
    try {
      await initSync(repoUrl)
      loadSettings()
    } catch (error) {
      console.error('Failed to init repo:', error)
      alert('Failed to initialize repository: ' + (error.response?.data?.detail || error.message))
    } finally {
      setSyncing(false)
    }
  }
  
  const handlePush = async () => {
    setSyncing(true)
    try {
      const res = await pushChanges()
      alert(res.data.message || 'Push successful')
      loadSettings()
    } catch (error) {
      console.error('Failed to push:', error)
      alert('Failed to push: ' + (error.response?.data?.detail || error.message))
    } finally {
      setSyncing(false)
    }
  }
  
  const handlePull = async () => {
    setSyncing(true)
    try {
      const res = await pullChanges()
      alert(res.data.message || 'Pull successful')
      loadSettings()
    } catch (error) {
      console.error('Failed to pull:', error)
      alert('Failed to pull: ' + (error.response?.data?.detail || error.message))
    } finally {
      setSyncing(false)
    }
  }
  
  if (loading) {
    return <div className="text-gray-400">Loading...</div>
  }
  
  return (
    <div className="max-w-4xl">
      <h1 className="text-3xl font-bold mb-8">Settings</h1>
      
      {/* GitHub Sync */}
      <div className="bg-gray-800 rounded-lg p-6 mb-8">
        <h2 className="text-xl font-bold mb-4">GitHub Sync</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">
              Repository URL
            </label>
            <div className="flex gap-4">
              <input
                type="url"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                placeholder="https://github.com/username/repo.git"
                className="flex-1 bg-gray-700 border border-gray-600 rounded px-4 py-2"
                disabled={syncStatus?.is_git_repo}
              />
              {!syncStatus?.is_git_repo && (
                <button
                  onClick={handleInitRepo}
                  disabled={syncing}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 px-6 py-2 rounded font-medium transition-colors"
                >
                  {syncing ? 'Initializing...' : 'Initialize'}
                </button>
              )}
            </div>
          </div>
          
          {syncStatus?.is_git_repo && (
            <>
              <div className="flex items-center gap-4 py-2">
                <span className="text-green-400">✓ Connected</span>
                {syncStatus.pending_changes > 0 && (
                  <span className="text-yellow-400">
                    {syncStatus.pending_changes} pending changes
                  </span>
                )}
                {syncStatus.last_sync && (
                  <span className="text-gray-500">
                    Last sync: {new Date(syncStatus.last_sync).toLocaleString()}
                  </span>
                )}
              </div>
              
              <div className="flex gap-4">
                <button
                  onClick={handlePush}
                  disabled={syncing}
                  className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 px-6 py-2 rounded font-medium transition-colors"
                >
                  {syncing ? 'Syncing...' : 'Push to GitHub'}
                </button>
                <button
                  onClick={handlePull}
                  disabled={syncing}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 px-6 py-2 rounded font-medium transition-colors"
                >
                  {syncing ? 'Syncing...' : 'Pull from GitHub'}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
      
      {/* Image Generators */}
      <div className="bg-gray-800 rounded-lg p-6 mb-8">
        <h2 className="text-xl font-bold mb-4">Image Generators</h2>
        
        <div className="space-y-2">
          {generators.map(gen => (
            <div key={gen} className="flex items-center gap-4 py-2 border-b border-gray-700 last:border-0">
              <span className={`w-3 h-3 rounded-full ${gen === 'mock' ? 'bg-yellow-400' : 'bg-green-400'}`} />
              <span className="font-medium">{gen}</span>
              {gen === 'mock' && (
                <span className="text-sm text-gray-500">(Testing only - generates placeholder images)</span>
              )}
            </div>
          ))}
        </div>
        
        <div className="mt-4 p-4 bg-gray-900 rounded">
          <p className="text-sm text-gray-400 mb-2">
            To enable more generators, set environment variables:
          </p>
          <code className="text-xs text-green-400 block mb-1">STABILITY_API_KEY=your_key</code>
          <code className="text-xs text-green-400 block">REPLICATE_API_KEY=your_key</code>
        </div>
      </div>
      
      {/* Sync Log */}
      {syncLog.length > 0 && (
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">Sync History</h2>
          
          <div className="space-y-2">
            {syncLog.map(log => (
              <div key={log.id} className="flex items-center gap-4 py-2 border-b border-gray-700 last:border-0 text-sm">
                <span className={`w-2 h-2 rounded-full ${log.status === 'success' ? 'bg-green-400' : 'bg-red-400'}`} />
                <span className="font-medium w-16">{log.action}</span>
                <span className="text-gray-400 flex-1">
                  {log.commit_hash ? log.commit_hash.substring(0, 7) : '—'}
                </span>
                <span className="text-gray-500">
                  {new Date(log.created_at).toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* System Info */}
      <div className="mt-8 text-sm text-gray-500">
        <h3 className="font-medium text-gray-400 mb-2">System Info</h3>
        <p>Canon System v1.1.0</p>
        <p>Local-first with GitHub backup</p>
        <p>React + FastAPI + SQLite</p>
      </div>
    </div>
  )
}

export default Settings
