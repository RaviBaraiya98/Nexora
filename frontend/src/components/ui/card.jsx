import { cn } from '@/utils/cn'

export function Card({ className, ...props }) {
  return <div className={cn('rounded-2xl border border-border/70 bg-card/80 backdrop-blur-xl', className)} {...props} />
}

export function CardHeader({ className, ...props }) {
  return <div className={cn('flex items-center justify-between p-5', className)} {...props} />
}

export function CardTitle({ className, ...props }) {
  return <h3 className={cn('text-base font-medium tracking-tight text-foreground', className)} {...props} />
}

export function CardContent({ className, ...props }) {
  return <div className={cn('p-5 pt-0', className)} {...props} />
}
