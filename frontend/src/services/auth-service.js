import { apiClient } from './api-client'

const TOKEN_KEY = 'nexora.access-token'
const USER_KEY = 'nexora.user'

function saveSession(payload) {
  localStorage.setItem(TOKEN_KEY, payload.accessToken)
  localStorage.setItem(USER_KEY, JSON.stringify(payload.user))
  return payload
}

export const authService = {
  async register(input) { return saveSession(await apiClient.post('/auth/register', input)) },
  async login(input) { return saveSession(await apiClient.post('/auth/login', input)) },
  async refresh() { return saveSession(await apiClient.post('/auth/refresh', {})) },
  async me() { return apiClient.get('/auth/me', { headers: { authorization: `Bearer ${authService.token()}` } }) },
  token() { return localStorage.getItem(TOKEN_KEY) },
  user() { return JSON.parse(localStorage.getItem(USER_KEY) || 'null') },
  async logout() { await apiClient.post('/auth/logout', {}).catch(() => null); localStorage.removeItem(TOKEN_KEY); localStorage.removeItem(USER_KEY) },
}
