import { useState, useEffect } from 'react'
import { getApprovalQueue, approveItem, rejectItem, regenerateAsset, getGenerators } from '../services/api'

function ApprovalQueue() {
  const [items, setItems] = useState([])
  const [generators, setGenerators] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedItem, setSelectedItem] = useState(null)
  const [rejectNotes, setRejectNotes] = useState('')
  const [selectedGenerator, setSelectedGenerator] = useState('mock')
  
  useEffect(() => {
    loadQueue()
    loadGenerators()
  }, [])
  
  const loadQueue = async () => {
    try {
      const res = await getApprovalQueue('pending')
      setItems(res.data)
    } catch (error) {
      console.error('Failed to load queue:', error)
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
  
  const handleApprove = async (itemId) => {
    try {
      await approveItem(itemId)
      setItems(items.filter(i => i.id !== itemId))
      setSelectedItem(null)
    } catch (error) {
      console.error('Failed to approve:', error)
      alert('Failed to approve item')
    }
  }
  
  const handleReject = async (itemId, assetId) => {
    try {
      await rejectItem(itemId, rejectNotes)
      
      // Trigger regeneration if notes provided
      if (rejectNotes && assetId) {
        await regenerateAsset(assetId, rejectNotes, selectedGenerator)
      }
      
      setItems(items.filter(i => i.id !== itemId))
      setSelectedItem(null)
      setRejectNotes('')
    } catch (error) {
      console.error('Failed to reject:', error)
      alert('Failed to reject item')
    }
  }
  
  const handleApproveAll = async () => {
    if (!confirm(`Approve all ${items.length} items?`)) return
    
    for (const item of items) {
      await approveItem(item.id)
    }
    loadQueue()
  }
  
  if (loading) {
    return <div className="text-gray-400">Loading...</div>
  }
  
  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Approval Queue</h1>
        {items.length > 0 && (
          <button
            onClick={handleApproveAll}
            className="bg-green-600 hover:bg-green-700 px-6 py-2 rounded-lg font-medium transition-colors"
          >
            Approve All ({items.length})
          </button>
        )}
      </div>
      
      {items.length === 0 ? (
        <div className="bg-gray-800 rounded-lg p-8 text-center">
          <p className="text-gray-400 text-xl mb-2">🎉 All caught up!</p>
          <p className="text-gray-500">No items pending approval</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Queue List */}
          <div className="space-y-4">
            {items.map(item => (
              <div
                key={item.id}
                onClick={() => setSelectedItem(item)}
                className={`bg-gray-800 rounded-lg p-4 cursor-pointer transition-colors ${
                  selectedItem?.id === item.id ? 'ring-2 ring-blue-500' : 'hover:bg-gray-750'
                }`}
              >
                <div className="flex items-center gap-4">
                  {/* Thumbnail */}
                  <div className="w-20 h-20 bg-gray-700 rounded flex-shrink-0 flex items-center justify-center overflow-hidden">
                    {item.asset?.file_path ? (
                      <img
                        src={`/files/characters/${item.asset.character_id}/${item.asset.asset_type}/${item.asset.asset_code}.png`}
                        alt=""
                        className="max-w-full max-h-full object-contain"
                        onError={(e) => e.target.style.display = 'none'}
                      />
                    ) : (
                      <span className="text-gray-500 text-2xl">?</span>
                    )}
                  </div>
                  
                  {/* Info */}
                  <div className="flex-1">
                    <h3 className="font-bold">{item.character_name}</h3>
                    <p className="text-sm text-gray-400">
                      {item.asset?.asset_type} / {item.asset?.asset_code}
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(item.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          {/* Detail Panel */}
          <div className="bg-gray-800 rounded-lg p-6">
            {selectedItem ? (
              <>
                <h2 className="text-xl font-bold mb-4">
                  {selectedItem.character_name} - {selectedItem.asset?.asset_type} / {selectedItem.asset?.asset_code}
                </h2>
                
                {/* Image Preview */}
                <div className="bg-gray-700 rounded-lg p-4 mb-4 flex items-center justify-center min-h-[300px]">
                  {selectedItem.asset?.file_path ? (
                    <img
                      src={`/files/characters/${selectedItem.asset.character_id}/${selectedItem.asset.asset_type}/${selectedItem.asset.asset_code}.png`}
                      alt=""
                      className="max-w-full max-h-[400px] object-contain"
                    />
                  ) : (
                    <span className="text-gray-500">No image available</span>
                  )}
                </div>
                
                {/* Prompt Used */}
                {selectedItem.asset?.prompt_used && (
                  <div className="mb-4">
                    <h4 className="text-sm font-medium text-gray-400 mb-1">Prompt Used</h4>
                    <pre className="text-xs bg-gray-900 p-3 rounded overflow-auto max-h-32">
                      {selectedItem.asset.prompt_used}
                    </pre>
                  </div>
                )}
                
                {/* Rejection Notes */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-400 mb-1">
                    Feedback (for regeneration)
                  </label>
                  <textarea
                    value={rejectNotes}
                    onChange={(e) => setRejectNotes(e.target.value)}
                    placeholder="Optional: Describe what needs to change..."
                    rows={3}
                    className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm"
                  />
                </div>
                
                {/* Generator Selection */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-400 mb-1">
                    Regeneration Tool
                  </label>
                  <select
                    value={selectedGenerator}
                    onChange={(e) => setSelectedGenerator(e.target.value)}
                    className="bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm"
                  >
                    {generators.map(g => (
                      <option key={g} value={g}>{g}</option>
                    ))}
                  </select>
                </div>
                
                {/* Actions */}
                <div className="flex gap-4">
                  <button
                    onClick={() => handleApprove(selectedItem.id)}
                    className="flex-1 bg-green-600 hover:bg-green-700 py-3 rounded-lg font-medium transition-colors"
                  >
                    ✓ Approve
                  </button>
                  <button
                    onClick={() => handleReject(selectedItem.id, selectedItem.asset?.id)}
                    className="flex-1 bg-red-600 hover:bg-red-700 py-3 rounded-lg font-medium transition-colors"
                  >
                    ✗ Reject & Regenerate
                  </button>
                </div>
              </>
            ) : (
              <div className="text-center text-gray-500 py-12">
                Select an item to review
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default ApprovalQueue
