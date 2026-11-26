import { cn } from '@/utils/cn'

export function Textarea({ className, ...props }) {
  return (
    <textarea
      className={cn(
        'min-h-28 w-full rounded-xl border border-border bg-muted/40 px-3 py-2 text-sm text-foreground outline-none ring-accent/40 placeholder:text-muted-foreground focus-visible:ring-2',
        className,
      )}
      {...props}
    />
  )
}
