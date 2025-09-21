import { useMutation } from '@tanstack/react-query'
import { api, setAccessToken } from '@/lib/api'
import type { User } from '@/stores/auth'

export interface LoginResponse {
  token: string
  user: User
}

export interface RegisterData {
  name: string
  email: string
  password: string
}

export interface LoginData {
  email: string
  password: string
}

// Plain functions
export async function login(email: string, password: string): Promise<LoginResponse> {
  const r = await api.post('/auth/login', { email, password })
  setAccessToken(r.data.access_token)
  const me = await api.get('/auth/me')
  return { token: r.data.access_token, user: me.data }
}

export async function register(name: string, email: string, password: string): Promise<boolean> {
  await api.post('/auth/register', { name, email, password })
  return true
}

export async function logout(): Promise<boolean> {
  try {
    await api.post('/auth/logout')
  } catch {
    // Ignore logout errors
  }
  setAccessToken(null)
  return true
}

// React Query hooks
export function useLogin() {
  return useMutation({
    mutationFn: ({ email, password }: LoginData) => login(email, password),
  })
}

export function useRegister() {
  return useMutation({
    mutationFn: ({ name, email, password }: RegisterData) => register(name, email, password),
  })
}

export function useLogout() {
  return useMutation({
    mutationFn: logout,
  })
}