import { Sparkles } from 'lucide-react'

export function BrandMark() {
  return (
    <div className="inline-flex items-center gap-2">
      <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-accent/60 bg-accent text-accent-foreground shadow-[0_8px_30px_rgba(224,168,77,0.16)]">
        <Sparkles size={16} />
      </div>
      <span className="text-sm font-semibold tracking-[0.2em] text-foreground">NEXORA</span>
    </div>
  )
}
