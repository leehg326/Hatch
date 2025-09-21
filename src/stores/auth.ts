import { setAccessToken, getAccessToken } from '@/lib/api'

export type User = { id: number; email: string; name: string; role: string }

let currentUser: User | null = null

export const authStore = {
  getUser(): User | null {
    return currentUser
  },
  getToken(): string | null {
    return getAccessToken()
  },
  set(user: User, token: string) {
    currentUser = user
    setAccessToken(token)
  },
  clear() {
    currentUser = null
    setAccessToken(null)
  },
}



