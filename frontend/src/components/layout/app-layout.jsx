import { BrandMark } from '@/components/common/brand-mark'
import { SidebarNav } from '@/components/layout/sidebar-nav'
import { Outlet } from 'react-router-dom'

export function AppLayout() {
  return (
    <div className="relative min-h-screen bg-background text-foreground">
      <div className="pointer-events-none fixed inset-0 -z-10 bg-[radial-gradient(circle_at_10%_10%,rgba(224,168,77,0.08),transparent_35%),radial-gradient(circle_at_90%_20%,rgba(91,141,184,0.1),transparent_38%)]" />
      <div className="mx-auto grid max-w-[1440px] grid-cols-1 gap-6 px-4 py-6 lg:grid-cols-[250px_1fr] lg:px-8">
        <aside className="rounded-2xl border border-border/70 bg-card/70 p-4 backdrop-blur-xl lg:sticky lg:top-6 lg:h-[calc(100vh-3rem)]">
          <div className="mb-6">
            <BrandMark />
          </div>
          <SidebarNav />
        </aside>
        <main className="rounded-2xl border border-border/70 bg-card/50 p-5 backdrop-blur-xl lg:p-7">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
