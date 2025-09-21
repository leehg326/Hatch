import { Suspense, lazy, Component, type ReactNode } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import ProtectedRoute from '@/routes/ProtectedRoute'
import AuthPage from '@/pages/AuthPage'
import VerifyEmail from '@/pages/VerifyEmail'
import ResetPassword from '@/pages/ResetPassword'
import OAuthComplete from '@/pages/OAuthComplete'
import AppLayout from '@/ui/AppLayout'
import ErrorFallback from '@/components/ErrorFallback'
import NotFound from '@/pages/NotFound'
// @ts-ignore
import Login from '@/pages/Login'
// @ts-ignore
import Signup from '@/pages/Signup'

const Dashboard = lazy(() => import('@/views/Dashboard'))
const Contracts = lazy(() => import('@/views/Contracts'))
const Clients = lazy(() => import('@/views/Clients'))
const Schedule = lazy(() => import('@/views/Schedule'))

function ProtectedLayout() {
  return (
    <ProtectedRoute>
      <AppLayout />
    </ProtectedRoute>
  )
}

class ErrorBoundaryLike extends Component<{ children: ReactNode }, { hasError: boolean; error?: any }> {
  constructor(props: { children: ReactNode }) {
    super(props)
    this.state = { hasError: false }
  }
  static getDerivedStateFromError(error: any) {
    return { hasError: true, error }
  }
  componentDidCatch(error: any) {
    // eslint-disable-next-line no-console
    console.error(error)
  }
  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} />
    }
    return this.props.children
  }
}

export default function App() {
  return (
    <ErrorBoundaryLike>
      <Routes>
        <Route path="/auth" element={<AuthPage />} />
        <Route path="/login" element={<Navigate to="/auth" replace />} />
        <Route path="/email-login" element={<Navigate to="/auth?mode=email" replace />} />
        <Route path="/basic-login" element={<Navigate to="/auth" replace />} />
        <Route path="/verify-email" element={<VerifyEmail />} />
        <Route path="/forgot-password" element={<Navigate to="/auth?mode=email" replace />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/oauth-complete" element={<OAuthComplete />} />
        <Route path="/register" element={<Navigate to="/auth?mode=email" replace />} />

        {/* Public route for Dashboard */}
        <Route path="/" element={<AppLayout />}>
          <Route index element={<Suspense fallback={null}><Dashboard /></Suspense>} />
        </Route>

        {/* Protected routes */}
        <Route element={<ProtectedLayout />}>
          <Route path="contracts" element={<Suspense fallback={null}><Contracts /></Suspense>} />
          <Route path="clients" element={<Suspense fallback={null}><Clients /></Suspense>} />
          <Route path="schedule" element={<Suspense fallback={null}><Schedule /></Suspense>} />
        </Route>

        {/* Email/Password Authentication Routes */}
        <Route path="/new-login" element={<Navigate to="/auth" replace />} />
        <Route path="/new-signup" element={<Signup />} />

        <Route path="*" element={<NotFound />} />
      </Routes>
    </ErrorBoundaryLike>
  )
}