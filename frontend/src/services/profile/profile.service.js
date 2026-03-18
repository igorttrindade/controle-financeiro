import { API_URL, apiRequest } from '@/services/http/api'

function authHeader() {
  const token = localStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export async function getMyProfile(options = {}) {
  return apiRequest('/api/users/me/profile', 'GET', null, options)
}

export async function updateMyProfile(payload, options = {}) {
  return apiRequest('/api/users/me/profile', 'PATCH', payload, options)
}

export async function uploadMyAvatar(file) {
  const formData = new FormData()
  formData.append('avatar', file)

  const response = await fetch(`${API_URL}/api/users/me/avatar`, {
    method: 'POST',
    headers: {
      ...authHeader(),
    },
    body: formData,
  })

  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    const error = new Error(data?.error || 'Falha ao enviar avatar')
    error.response = { status: response.status, data }
    throw error
  }

  return data
}

export async function deleteMyAvatar(options = {}) {
  return apiRequest('/api/users/me/avatar', 'DELETE', null, options)
}

export async function fetchMyAvatarObjectUrl() {
  const token = localStorage.getItem('token')
  if (!token) return null

  const response = await fetch(`${API_URL}/api/users/me/avatar`, {
    headers: {
      ...authHeader(),
    },
  })

  if (response.status === 404) {
    return null
  }

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    const error = new Error(data?.error || 'Falha ao carregar avatar')
    error.response = { status: response.status, data }
    throw error
  }

  const blob = await response.blob()
  return URL.createObjectURL(blob)
}

export async function requestSecurityChange(payload, options = {}) {
  return apiRequest('/api/users/me/security/request', 'POST', payload, options)
}

export async function confirmSecurityChange(payload, options = {}) {
  return apiRequest('/api/users/me/security/confirm', 'POST', payload, options)
}
