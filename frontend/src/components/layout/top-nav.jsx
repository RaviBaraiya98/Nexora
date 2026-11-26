import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Bell, Search } from 'lucide-react'

export function TopNav({ title, subtitle }) {
  return (
    <header className="mb-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">{title}</h1>
        <p className="text-sm text-muted-foreground">{subtitle}</p>
      </div>
      <div className="flex items-center gap-3">
        <div className="relative hidden w-64 md:block">
          <Search size={16} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <Input className="pl-9" placeholder="Search companies, topics, reports" aria-label="Search" />
        </div>
        <button
          className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-border bg-card text-muted-foreground transition-colors hover:text-foreground"
          aria-label="Notifications"
        >
          <Bell size={16} />
        </button>
        <Badge className="border-accent/20 bg-accent/10 text-accent">AI Sync Active</Badge>
      </div>
    </header>
  )
}
