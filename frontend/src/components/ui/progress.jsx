import { cn } from '@/utils/cn'

export function Progress({ className, value = 0 }) {
  return (
    <div className={cn('h-2.5 w-full overflow-hidden rounded-full bg-muted', className)}>
      <div
        className="h-full rounded-full bg-gradient-to-r from-accent to-accent-2 transition-all duration-500"
        style={{ width: `${Math.max(0, Math.min(100, value))}%` }}
      />
    </div>
  )
}
