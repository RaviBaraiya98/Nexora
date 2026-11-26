import { ROUTE_PATHS } from '@/constants/route-paths'
import {
    BarChart3,
    Building2,
    FileBarChart2,
    LayoutDashboard,
    Settings,
    Sparkles,
    UserCircle2,
} from 'lucide-react'

export const appNavItems = [
  { label: 'Dashboard', to: ROUTE_PATHS.DASHBOARD, icon: LayoutDashboard },
  { label: 'Profile', to: ROUTE_PATHS.PROFILE, icon: UserCircle2 },
  { label: 'Companies', to: ROUTE_PATHS.COMPANIES, icon: Building2 },
  { label: 'Interview', to: ROUTE_PATHS.INTERVIEW, icon: Sparkles },
  { label: 'Reports', to: ROUTE_PATHS.REPORTS, icon: FileBarChart2 },
  { label: 'Analytics', to: ROUTE_PATHS.ANALYTICS, icon: BarChart3 },
  { label: 'Settings', to: ROUTE_PATHS.SETTINGS, icon: Settings },
]
