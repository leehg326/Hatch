import axios, { AxiosError } from 'axios'
import type { AxiosRequestConfig } from 'axios'

let accessToken: string | null = null

export const getAccessToken = () => accessToken
export const setAccessToken = (token: string | null) => {
  accessToken = token
}

export const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
  timeout: 8000
})

function getCookie(name: string): string | null {
  if (typeof document === 'undefined') return null
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop()!.split(';').shift() || null
  return null
}

api.interceptors.request.use((config) => {
  const token = accessToken
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (resp) => resp,
  async (error: AxiosError) => {
    const original = error.config as (AxiosRequestConfig & { _retry?: boolean }) | undefined
    if (!original) throw error

    const status = error.response?.status
    const url = original.url || ''
    
    // Only retry on 401, not for auth endpoints, and not already retried
    if (status === 401 && !url.includes('/auth/') && !original._retry) {
      original._retry = true
      try {
        const csrf = getCookie('csrf_refresh_token')
        const refreshResp = await api.post<{ access_token: string }>(
          '/auth/refresh',
          undefined,
          { headers: csrf ? { 'X-CSRF-TOKEN': csrf } : undefined }
        )
        const newToken = refreshResp.data?.access_token
        if (newToken) {
          setAccessToken(newToken)
          original.headers = original.headers || {}
          original.headers.Authorization = `Bearer ${newToken}`
          return api.request(original)
        }
      } catch (_e) {
        // Refresh failed, clear token and reject
        setAccessToken(null)
      }
    }
    throw error
  }
)