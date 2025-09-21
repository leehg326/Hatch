export type CurrentUser = {
  id: string
  name: string
}

const STORAGE_KEY = 'currentUser'

export function getCurrentUser(): CurrentUser | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw) as CurrentUser
    if (parsed && typeof parsed.name === 'string') return parsed
    return null
  } catch {
    return null
  }
}





