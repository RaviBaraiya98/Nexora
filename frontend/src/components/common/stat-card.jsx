import { Card, CardContent } from '@/components/ui/card'
import { motion } from 'framer-motion'

export function StatCard({ label, value, suffix = '', delta }) {
  return (
    <motion.div whileHover={{ y: -4 }} transition={{ duration: 0.2 }}>
      <Card className="relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(91,140,255,0.15),transparent_55%)]" />
        <CardContent className="space-y-2 pt-5">
          <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">{label}</p>
          <p className="text-3xl font-semibold text-foreground">
            {value}
            <span className="text-lg text-muted-foreground">{suffix}</span>
          </p>
          <p className="text-xs text-accent">{delta}</p>
        </CardContent>
      </Card>
    </motion.div>
  )
}
