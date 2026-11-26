import { BrandMark } from '@/components/common/brand-mark'
import { Button } from '@/components/ui/button'
import { ROUTE_PATHS } from '@/constants/route-paths'
import { Link, Outlet } from 'react-router-dom'

export function PublicLayout() {
  return (
    <div className="relative min-h-screen bg-background text-foreground">
      <div className="pointer-events-none fixed inset-0 -z-10 bg-[radial-gradient(circle_at_20%_20%,rgba(224,168,77,0.08),transparent_32%),radial-gradient(circle_at_80%_30%,rgba(91,141,184,0.1),transparent_34%)]" />
      <header className="mx-auto flex max-w-7xl items-center justify-between border-b border-border/60 px-4 py-5 lg:px-8">
        <BrandMark />
        <nav className="hidden items-center gap-6 text-sm text-muted-foreground md:flex">
          <a href="/#story" className="transition-colors hover:text-foreground">How it works</a>
          <Link to={ROUTE_PATHS.LOGIN} className="transition-colors hover:text-foreground">Login</Link>
          <Link to={ROUTE_PATHS.INTERVIEW}><Button size="sm">Start interview</Button></Link>
        </nav>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  )
}
