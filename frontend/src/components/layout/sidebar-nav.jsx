import { appNavItems } from '@/constants/navigation'
import { cn } from '@/utils/cn'
import { NavLink } from 'react-router-dom'

export function SidebarNav() {
  return (
    <nav className="space-y-2">
      {appNavItems.map((item) => {
        const Icon = item.icon
        return (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              cn(
                'group flex items-center gap-3 rounded-xl border border-transparent px-3 py-2 text-sm transition-all duration-200',
                isActive
                  ? 'border-border bg-muted/70 text-foreground'
                  : 'text-muted-foreground hover:border-border/70 hover:bg-muted/50 hover:text-foreground',
              )
            }
          >
            <Icon size={16} className="transition-transform duration-200 group-hover:scale-105" />
            <span>{item.label}</span>
          </NavLink>
        )
      })}
    </nav>
  )
}
