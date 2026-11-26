import { cn } from '@/utils/cn'

export function SectionHeader({ title, subtitle, className }) {
  return (
    <div className={cn('space-y-1', className)}>
      <h2 className="text-lg font-semibold tracking-tight text-foreground">{title}</h2>
      {subtitle ? <p className="text-sm text-muted-foreground">{subtitle}</p> : null}
    </div>
  )
}
