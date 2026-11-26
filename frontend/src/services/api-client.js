const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:4000/api'
const TOKEN_KEY = 'nexora.access-token'

async function request(path, options = {}, canRefresh = true) {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    credentials: 'include',
    headers: { ...(options.body instanceof FormData ? {} : { 'content-type': 'application/json' }), ...(localStorage.getItem(TOKEN_KEY) ? { authorization: `Bearer ${localStorage.getItem(TOKEN_KEY)}` } : {}), ...(options.headers || {}) },
  })
  const payload = await response.json().catch(() => ({}))
  if (response.status === 401 && canRefresh && !path.startsWith('/auth/')) {
    const refreshed = await request('/auth/refresh', { method: 'POST' }, false).catch(() => null)
    if (refreshed?.accessToken) {
      localStorage.setItem(TOKEN_KEY, refreshed.accessToken)
      return request(path, options, false)
    }
  }
  if (!response.ok) {
    const detail = Array.isArray(payload.details) ? payload.details.map((item) => `${item.path?.join('.') || 'field'}: ${item.message}`).join('; ') : ''
    throw new Error(detail ? `${payload.error || 'Request failed'} - ${detail}` : (payload.error || 'Request failed'))
  }
  return payload
}

export const apiClient = {
  request,
  get(path, options) { return request(path, { ...options, method: 'GET' }) },
  post(path, body, options) { return request(path, { ...options, method: 'POST', body: JSON.stringify(body) }) },
}
