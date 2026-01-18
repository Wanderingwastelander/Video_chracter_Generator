import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Characters
export const getCharacters = () => api.get('/characters')
export const getCharacter = (id) => api.get(`/characters/${id}`)
export const createCharacter = (formData) => api.post('/characters', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
export const updateCharacter = (id, formData) => api.put(`/characters/${id}`, formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
export const deleteCharacter = (id) => api.delete(`/characters/${id}`)
export const getCharacterPrompts = (id) => api.get(`/characters/${id}/prompts`)

// Generation
export const getGenerators = () => api.get('/generate/generators')
export const generateCharacterAssets = (characterId, options) => 
  api.post(`/generate/character/${characterId}`, null, { params: options })
export const getGenerationJobs = (params) => api.get('/generate/jobs', { params })
export const regenerateAsset = (assetId, feedback, generator) => 
  api.post(`/generate/regenerate/${assetId}`, null, { params: { feedback, generator } })

// Approval
export const getApprovalQueue = (status = 'pending', characterId = null) => 
  api.get('/approval/queue', { params: { status, character_id: characterId } })
export const approveItem = (itemId, notes = null) => 
  api.post(`/approval/approve/${itemId}`, null, { params: { notes } })
export const rejectItem = (itemId, notes = null) => 
  api.post(`/approval/reject/${itemId}`, null, { params: { notes } })
export const getApprovalStats = () => api.get('/approval/stats')
export const bulkApprove = (itemIds) => api.post('/approval/bulk-approve', itemIds)

// Environments
export const getEnvironments = () => api.get('/environments')
export const getEnvironment = (id) => api.get(`/environments/${id}`)
export const createEnvironment = (formData) => api.post('/environments', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
export const deleteEnvironment = (id) => api.delete(`/environments/${id}`)

// Sync
export const getSyncStatus = () => api.get('/sync/status')
export const initSync = (remoteUrl) => api.post('/sync/init', null, { params: { remote_url: remoteUrl } })
export const pushChanges = (message) => api.post('/sync/push', null, { params: { message } })
export const pullChanges = () => api.post('/sync/pull')
export const getSyncLog = (limit = 20) => api.get('/sync/log', { params: { limit } })

// Health
export const healthCheck = () => api.get('/health')

export default api
