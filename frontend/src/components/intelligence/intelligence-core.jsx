import { motion } from 'framer-motion'

const nodes = [
  { label: 'Student', x: '10%', y: '50%' },
  { label: 'Interview', x: '31%', y: '25%' },
  { label: 'Analysis', x: '52%', y: '50%' },
  { label: 'Skill gap', x: '73%', y: '25%' },
  { label: 'Progress', x: '90%', y: '50%' },
]

export function IntelligenceCore() {
  return (
    <div className="relative h-36 overflow-hidden border-y border-border py-5">
      <svg className="absolute inset-0 h-full w-full" viewBox="0 0 100 40" preserveAspectRatio="none" aria-hidden="true">
        <motion.path d="M 8 20 C 18 20, 20 10, 29 10 S 42 30, 50 20 S 63 10, 71 10 S 83 20, 92 20" fill="none" stroke="var(--accent-2)" strokeDasharray="1 3" strokeWidth="0.35" initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 0.8 }} transition={{ duration: 1.8 }} />
      </svg>
      {nodes.map((node, index) => (
        <motion.div key={node.label} initial={{ opacity: 0, scale: 0.7 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: index * 0.14 }} className="absolute -translate-x-1/2 -translate-y-1/2 text-center" style={{ left: node.x, top: node.y }}>
          <div className={`mx-auto h-3 w-3 rounded-full border-2 ${node.label === 'Skill gap' ? 'border-accent bg-accent' : 'border-accent-2 bg-background'}`} />
          <p className="mt-2 font-data text-[0.58rem] uppercase tracking-wider text-muted-foreground">{node.label}</p>
        </motion.div>
      ))}
    </div>
  )
}
