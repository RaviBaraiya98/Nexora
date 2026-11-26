import { ROUTE_PATHS } from '@/constants/route-paths'
import { useAuth } from '@/context/auth-context'
import { Navigate, Outlet, useLocation } from 'react-router-dom'

export function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth()
  const location = useLocation()
  if (isLoading) return <div className="min-h-screen bg-background" aria-busy="true" />
  if (!isAuthenticated) return <Navigate to={ROUTE_PATHS.LOGIN} replace state={{ from: location.pathname }} />
  return <Outlet />
}
