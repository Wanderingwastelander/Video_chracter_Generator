import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getCharacters, getApprovalStats, getSyncStatus } from '../services/api'

function Dashboard() {
  const [stats, setStats] = useState({
    characters: 0,
    pendingApprovals: 0,
    syncStatus: null
  })
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    loadStats()
  }, [])
  
  const loadStats = async () => {
    try {
      const [charsRes, approvalRes, syncRes] = await Promise.all([
        getCharacters(),
        getApprovalStats(),
        getSyncStatus()
      ])
      
      setStats({
        characters: charsRes.data.length,
        pendingApprovals: approvalRes.data.pending,
        syncStatus: syncRes.data
      })
    } catch (error) {
      console.error('Failed to load stats:', error)
    } finally {
      setLoading(false)
    }
  }
  
  if (loading) {
    return <div className="text-gray-400">Loading...</div>
  }
  
  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>
      
      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-gray-400 text-sm uppercase">Characters</h3>
          <p className="text-4xl font-bold text-blue-400">{stats.characters}</p>
          <Link to="/characters" className="text-sm text-blue-500 hover:underline">
            View all →
          </Link>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-gray-400 text-sm uppercase">Pending Approvals</h3>
          <p className="text-4xl font-bold text-yellow-400">{stats.pendingApprovals}</p>
          <Link to="/approval" className="text-sm text-blue-500 hover:underline">
            Review →
          </Link>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-gray-400 text-sm uppercase">Sync Status</h3>
          <p className="text-xl font-bold text-green-400">
            {stats.syncStatus?.is_git_repo ? 'Connected' : 'Not Configured'}
          </p>
          {stats.syncStatus?.pending_changes > 0 && (
            <p className="text-sm text-yellow-400">
              {stats.syncStatus.pending_changes} pending changes
            </p>
          )}
        </div>
      </div>
      
      {/* Quick Actions */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
        <div className="flex flex-wrap gap-4">
          <Link
            to="/characters/new"
            className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-medium transition-colors"
          >
            + New Character
          </Link>
          
          {stats.pendingApprovals > 0 && (
            <Link
              to="/approval"
              className="bg-yellow-600 hover:bg-yellow-700 px-6 py-3 rounded-lg font-medium transition-colors"
            >
              Review {stats.pendingApprovals} Pending
            </Link>
          )}
        </div>
      </div>
      
      {/* System Info */}
      <div className="mt-8 text-sm text-gray-500">
        <p>Canon System v1.1.0</p>
        <p>Character and environment consistency system for AI-generated video production</p>
      </div>
    </div>
  )
}

export default Dashboard
