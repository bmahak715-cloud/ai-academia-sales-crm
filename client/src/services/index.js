import api from './api'

export const authApi = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  logout: () => api.post('/auth/logout'),
  me: () => api.get('/auth/me'),
  users: () => api.get('/auth/users'),
}

export const institutionsApi = {
  list: (params) => api.get('/institutions', { params }),
  get: (id) => api.get(`/institutions/${id}`),
  create: (data) => api.post('/institutions', data),
  update: (id, data) => api.put(`/institutions/${id}`, data),
  delete: (id) => api.delete(`/institutions/${id}`),
  updateStatus: (id, lead_status) => api.patch(`/institutions/${id}/status`, { lead_status }),
  assign: (id, assigned_to_id) => api.patch(`/institutions/${id}/assign`, { assigned_to_id }),
  analyze: (id) => api.post(`/institutions/${id}/analyze`),
  regenerateOutreach: (id) => api.post(`/institutions/${id}/regenerate-outreach`),
}

export const followUpsApi = {
  list: (params) => api.get('/follow-ups', { params }),
  create: (data) => api.post('/follow-ups', data),
  update: (id, data) => api.put(`/follow-ups/${id}`, data),
  delete: (id) => api.delete(`/follow-ups/${id}`),
  complete: (id) => api.patch(`/follow-ups/${id}/complete`),
}

export const meetingsApi = {
  list: (params) => api.get('/meetings', { params }),
  create: (data) => api.post('/meetings', data),
  update: (id, data) => api.put(`/meetings/${id}`, data),
  delete: (id) => api.delete(`/meetings/${id}`),
  complete: (id, data) => api.patch(`/meetings/${id}/complete`, data),
}

export const communicationsApi = {
  list: (params) => api.get('/communications', { params }),
  generate: (data) => api.post('/communications/generate', data),
  send: (data) => api.post('/communications/send', data),
  markSent: (id, data) => api.patch(`/communications/${id}/mark-sent`, data),
}

export const dashboardApi = {
  get: () => api.get('/dashboard'),
  reports: () => api.get('/reports'),
}

export const notificationsApi = {
  list: () => api.get('/notifications'),
  markRead: (id) => api.patch(`/notifications/${id}/read`),
  markAllRead: () => api.patch('/notifications/read-all'),
}
