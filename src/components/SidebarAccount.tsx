import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { Settings, CreditCard, Users, LogOut, LogIn } from 'lucide-react'
import { useLogout } from '@/features/auth/api'
import type { User } from '@/stores/auth'
import { getAccessToken } from '@/lib/api'
import { authStore } from '@/stores/auth'
import { useAuth } from '@/auth/AuthProvider.tsx'

function getInitials(name?: string): string {
  if (!name) return 'H'
  const parts = name.trim().split(/\s+/)
  const first = parts[0]?.[0] || ''
  const second = parts[1]?.[0] || ''
  return (first + second || first || 'H').toUpperCase()
}

export default function SidebarAccount({ user }: { user: User | null }) {
  const navigate = useNavigate()
  const logoutMutation = useLogout()
  const { user: authUser, logout: authLogout } = useAuth()

  // Use new auth user if available, fallback to old user
  const displayUser = authUser || user
  const initials = useMemo(() => getInitials(displayUser?.name), [displayUser?.name])
  const isAuthed = Boolean(authUser) || Boolean(getAccessToken()) || Boolean(authStore.getToken())

  const onSignOut = async () => {
    if (authUser) {
      // Use new auth system
      await authLogout()
      navigate('/login', { replace: true })
    } else {
      // Use old auth system
      await logoutMutation.mutateAsync()
      navigate('/auth?tab=login', { replace: true })
    }
  }

  const goLogin = () => navigate('/new-login')

  return (
    <div className="space-y-1">
      <button className="flex items-center gap-3 px-2 py-2 rounded-md hover:bg-muted transition text-sm" onClick={() => navigate('/settings') }>
        <Settings size={16} />
        <span>설정</span>
      </button>
      <button className="flex items-center gap-3 px-2 py-2 rounded-md hover:bg-muted transition text-sm" onClick={() => navigate('/billing') }>
        <CreditCard size={16} />
        <span>구독 관리</span>
      </button>
      <button className="flex items-center gap-3 px-2 py-2 rounded-md hover:bg-muted transition text-sm" onClick={() => navigate('/accounts') }>
        <Users size={16} />
        <span>계정 전환</span>
      </button>

      <div className="h-px bg-gray-100 my-1" />

      {!isAuthed ? (
        <button className="flex items-center gap-3 px-2 py-2 rounded-md transition text-sm text-blue-700 hover:bg-blue-50" onClick={goLogin}>
          <LogIn size={16} />
          <span>로그인</span>
        </button>
      ) : (
        <button className="flex items-center gap-3 px-2 py-2 rounded-md transition text-sm text-gray-700 hover:bg-gray-100" onClick={onSignOut}>
          <LogOut size={16} />
          <span>로그아웃</span>
        </button>
      )}

      {displayUser && (
        <div className="mt-3 flex items-center gap-3">
          <div className="h-8 w-8 rounded-full bg-gray-100 text-gray-700 grid place-items-center text-xs font-semibold">
            {initials}
          </div>
          <div className="min-w-0">
            <div className="text-sm font-medium truncate">{displayUser.name}</div>
            <div className="text-xs text-muted-foreground break-all">{displayUser.email}</div>
            <div className="mt-1 inline-flex items-center rounded-full bg-gray-100 px-2 py-0.5 text-[10px] text-gray-600">Personal Plan</div>
          </div>
        </div>
      )}
    </div>
  )
}


