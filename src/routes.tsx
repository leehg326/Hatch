import { lazy } from 'react'
import AppLayout from './ui/AppLayout'
import ProtectedRoute from '@/routes/ProtectedRoute'
import Login from '@/pages/Login'
import Register from '@/pages/Register'

const Dashboard = lazy(() => import('./views/Dashboard'))
const Contracts = lazy(() => import('./views/Contracts'))
const ContractForm = lazy(() => import('./views/ContractForm'))
const ContractPreview = lazy(() => import('./views/ContractPreview'))
const Clients = lazy(() => import('./views/Clients'))
const Schedule = lazy(() => import('./views/Schedule'))

const routes = [
  { path: '/login', element: <Login /> },
  { path: '/register', element: <Register /> },
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: 'contracts', element: <ProtectedRoute><Contracts /></ProtectedRoute> },
      { path: 'contracts/new', element: <ProtectedRoute><ContractForm /></ProtectedRoute> },
      { path: 'contracts/:id', element: <ProtectedRoute><ContractPreview /></ProtectedRoute> },
      { path: 'clients', element: <ProtectedRoute><Clients /></ProtectedRoute> },
      { path: 'schedule', element: <ProtectedRoute><Schedule /></ProtectedRoute> },
    ],
  },
]

export default routes



