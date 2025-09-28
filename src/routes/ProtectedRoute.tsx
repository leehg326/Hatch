import { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/auth/AuthProvider'

export default function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isAuthed, loading } = useAuth()
  const location = useLocation()
  
  // 로딩 중이면 로딩 표시
  if (loading) {
    return <div className="flex justify-center items-center min-h-screen">로딩 중...</div>
  }
  
  // 인증되지 않은 경우
  if (!isAuthed) {
    if (location.pathname.startsWith('/auth')) {
      return <>{children}</>
    }
    return <Navigate to="/auth?tab=login" replace />
  }
  
  return <>{children}</>
}