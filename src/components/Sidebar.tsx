import { NavLink } from 'react-router-dom'
import { Calendar, FileText, Users, LayoutDashboard, Sparkles } from 'lucide-react'
import { APP_NAME } from '@/lib/appConfig'
import { authStore } from '@/stores/auth'
import SidebarAccount from '@/components/SidebarAccount'
import { useAuth } from '@/auth/AuthProvider.tsx'

export default function Sidebar(){
  const { user: authUser } = useAuth()
  const user = authStore.getUser()
  const displayUser = authUser || user
  const items = [
    { to: '/', label: '대시보드', icon: LayoutDashboard },
    { to: '/oneclick-contract', label: '원클릭 계약서', icon: Sparkles },
    { to: '/contracts', label: '계약서 관리', icon: FileText },
    { to: '/clients', label: '고객', icon: Users },
    { to: '/schedule', label: '일정', icon: Calendar },
  ]
  return (
    <aside className="hidden md:flex h-screen w-64 flex-col border-none bg-white">
      <div className="p-4">
        <span className="block text-3xl font-extrabold tracking-tight bg-gradient-to-r from-blue-500 to-violet-600 bg-clip-text text-transparent">
          Hatch
        </span>
      </div>
      <nav className="px-3 pb-3 space-y-1">
        {items.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-2 py-2 rounded-md text-sm transition hover:bg-muted ${
                isActive ? 'bg-muted text-foreground' : 'text-muted-foreground'
              }`
            }
            end={to === '/'}
          >
            <Icon size={18} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="mt-auto border-none bg-white p-3">
        <SidebarAccount user={displayUser} />
      </div>
    </aside>
  )
}


