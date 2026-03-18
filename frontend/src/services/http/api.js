export const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000'
import axios from 'axios'

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export async function apiRequest(endpoint, method = 'GET', data = null, options = {}) {
  const requestConfig = {
    url: endpoint,
    method,
    ...options,
  }

  if (data !== null && data !== undefined) {
    requestConfig.data = data
  }

  const response = await api(requestConfig)
  return response.data
}
