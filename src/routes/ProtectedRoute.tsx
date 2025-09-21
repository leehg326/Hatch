import { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { getAccessToken } from '@/lib/api'

export default function ProtectedRoute({ children }: { children: ReactNode }) {
  const token = getAccessToken()
  const location = useLocation()
  
  if (!token) {
    if (location.pathname.startsWith('/auth')) {
      return <>{children}</>
    }
    return <Navigate to="/auth?tab=login" replace />
  }
  
  return <>{children}</>
}