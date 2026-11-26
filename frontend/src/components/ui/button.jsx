import { cn } from '@/utils/cn'
import { cva } from 'class-variance-authority'

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-xl font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:pointer-events-none disabled:opacity-40',
  {
    variants: {
      variant: {
        default: 'bg-accent text-accent-foreground shadow-[0_10px_30px_rgba(70,113,255,0.32)] hover:translate-y-[-1px] hover:brightness-110',
        ghost: 'text-foreground hover:bg-muted',
        outline: 'border border-border bg-card text-foreground hover:border-accent/50',
      },
      size: {
        default: 'h-10 px-4 py-2',
        lg: 'h-12 px-6 text-sm',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)

function Button({ className, variant, size, asChild = false, ...props }) {
  const Comp = asChild ? 'span' : 'button'
  return <Comp className={cn(buttonVariants({ variant, size, className }))} {...props} />
}

export { Button, buttonVariants }
