import { apiClient } from './api-client'
import { authService } from './auth-service'

function authOptions() {
  return { headers: { authorization: `Bearer ${authService.token()}` } }
}

export const interviewService = {
  build(input) { return apiClient.post('/interviews/build', input, authOptions()) },
  start(id) { return apiClient.post(`/interviews/${id}/start`, {}, authOptions()) },
  submitAnswer(interviewId, questionId, input) { return apiClient.post(`/interviews/${interviewId}/questions/${questionId}/answer`, input, authOptions()) },
  get(id) { return apiClient.get(`/interviews/${id}`, authOptions()) },
  list() { return apiClient.get('/interviews', authOptions()) },
  reports() { return apiClient.get('/interviews/reports', authOptions()) },
}

export async function uploadResume(file) {
  const body = new FormData()
  body.append('resume', file)
  const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://127.0.0.1:4000/api'}/profile/resume`, { method: 'POST', body, headers: { authorization: `Bearer ${authService.token()}` } })
  const payload = await response.json()
  if (!response.ok) throw new Error(payload.error || 'Resume upload failed')
  return payload
}

export async function reprocessResume() {
  return apiClient.post('/profile/resume/reprocess', {}, authOptions())
}

export async function updateProfile(profile) {
  return apiClient.request('/profile', { method: 'PATCH', body: JSON.stringify(profile), headers: { authorization: `Bearer ${authService.token()}` } })
}

export async function getProfile() {
  return apiClient.get('/profile', authOptions())
}
