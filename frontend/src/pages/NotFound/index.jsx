import { Button } from '@/components/ui/button'
import { ROUTE_PATHS } from '@/constants/route-paths'
import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="w-full max-w-lg rounded-2xl border border-border bg-card p-8 text-center">
        <p className="text-sm uppercase tracking-[0.3em] text-muted-foreground">404</p>
        <h1 className="mt-2 text-4xl font-semibold text-foreground">Page Not Found</h1>
        <p className="mt-3 text-sm text-muted-foreground">The route does not exist in your current workspace.</p>
        <Link to={ROUTE_PATHS.LANDING} className="mt-6 inline-block">
          <Button>Back to Landing</Button>
        </Link>
      </div>
    </div>
  )
}
