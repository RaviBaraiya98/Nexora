import { cn } from '@/utils/cn'

export function Input({ className, ...props }) {
  return (
    <input
      className={cn(
        'h-11 w-full rounded-xl border border-border bg-muted/40 px-3 text-sm text-foreground outline-none ring-accent/40 placeholder:text-muted-foreground focus-visible:ring-2',
        className,
      )}
      {...props}
    />
  )
}
