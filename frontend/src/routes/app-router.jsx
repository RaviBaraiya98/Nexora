import { AppLayout } from '@/components/layout/app-layout'
import { ProtectedRoute } from '@/components/layout/protected-route'
import { PublicLayout } from '@/components/layout/public-layout'
import { ROUTE_PATHS } from '@/constants/route-paths'
import { createBrowserRouter } from 'react-router-dom'

export const appRouter = createBrowserRouter([
  {
    element: <PublicLayout />,
    children: [
      {
        path: ROUTE_PATHS.LANDING,
        lazy: () => import('@/pages/Landing').then((module) => ({ Component: module.LandingPage })),
      },
      {
        path: ROUTE_PATHS.LOGIN,
        lazy: () => import('@/pages/Login').then((module) => ({ Component: module.LoginPage })),
      },
      {
        path: ROUTE_PATHS.REGISTER,
        lazy: () => import('@/pages/Register').then((module) => ({ Component: module.RegisterPage })),
      },
    ],
  },
  {
    element: <ProtectedRoute />,
    children: [
      { element: <AppLayout />, children: [
        {
          path: ROUTE_PATHS.DASHBOARD,
          lazy: () => import('@/pages/Dashboard').then((module) => ({ Component: module.DashboardPage })),
        },
      {
        path: ROUTE_PATHS.PROFILE,
        lazy: () => import('@/pages/Profile').then((module) => ({ Component: module.ProfilePage })),
      },
      {
        path: ROUTE_PATHS.COMPANIES,
        lazy: () => import('@/pages/Companies').then((module) => ({ Component: module.CompaniesPage })),
      },
      {
        path: ROUTE_PATHS.INTERVIEW,
        lazy: () => import('@/pages/Interview').then((module) => ({ Component: module.InterviewPage })),
      },
      {
        path: `${ROUTE_PATHS.INTERVIEW}/:interviewId`,
        lazy: () => import('@/pages/Interview').then((module) => ({ Component: module.InterviewPage })),
      },
      {
        path: ROUTE_PATHS.REPORTS,
        lazy: () => import('@/pages/Reports').then((module) => ({ Component: module.ReportsPage })),
      },
      {
        path: ROUTE_PATHS.ANALYTICS,
        lazy: () => import('@/pages/Analytics').then((module) => ({ Component: module.AnalyticsPage })),
      },
        {
          path: ROUTE_PATHS.SETTINGS,
          lazy: () => import('@/pages/Settings').then((module) => ({ Component: module.SettingsPage })),
        },
      ] },
    ],
  },
  {
    path: '*',
    lazy: () => import('@/pages/NotFound').then((module) => ({ Component: module.NotFoundPage })),
  },
])
