import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { motion } from 'framer-motion'

const metrics = [
  { label: 'Technical understanding', value: 86 },
  { label: 'Answer relevance', value: 91 },
  { label: 'Answer structure', value: 74 },
  { label: 'Communication', value: 78 },
]

const skills = [
  { label: 'Java', value: 86, expected: 90 },
  { label: 'OOP', value: 80, expected: 88 },
  { label: 'DBMS', value: 55, expected: 72 },
  { label: 'SQL', value: 32, expected: 75, priority: true },
]

export function InterviewReport({ compact = false, activeStage = 'report' }) {
  return (
    <motion.div
      layout
      className={`report-grid ink-surface relative overflow-hidden border border-border p-5 ${compact ? 'rounded-xl' : 'rounded-2xl'}`}
    >
      <div className="absolute right-5 top-5 report-mark">Live product preview</div>
      <div className="space-y-5">
        <div className="border-b border-border pb-4">
          <p className="eyebrow">Nexora interview report / 024</p>
          <div className="mt-3 flex flex-wrap items-end justify-between gap-3">
            <div>
              <h3 className="font-display text-2xl text-foreground">TCS · Java Developer</h3>
              <p className="mt-1 text-sm text-muted-foreground">Technical round · HashMap vs ConcurrentHashMap</p>
            </div>
            <div className="text-right">
              <p className="font-data text-3xl text-foreground">81<span className="text-base text-muted-foreground">/100</span></p>
              <p className="report-mark">readiness signal</p>
            </div>
          </div>
        </div>

        {activeStage === 'analysis' ? (
          <div className="grid gap-3 rounded-lg border border-accent/40 bg-accent/5 p-4">
            <p className="eyebrow">Answer becoming intelligence</p>
            <p className="text-sm leading-6 text-foreground">“I would use HashMap because it gives constant-time lookup and is useful for key-value access...”</p>
            <div className="flex flex-wrap gap-2">
              {['HashMap', 'Thread safety', 'Concurrency', 'Collections'].map((tag) => <Badge key={tag} className="border-accent/30 bg-accent/10 text-accent">{tag}</Badge>)}
            </div>
            <p className="text-xs text-muted-foreground"><span className="annotation">Missing signal:</span> concurrent modification behavior</p>
          </div>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2">
            {metrics.map((metric, index) => (
              <div key={metric.label} className="space-y-2">
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>{metric.label}</span>
                  <span className="font-data text-foreground">{metric.value}%</span>
                </div>
                <motion.div initial={{ scaleX: 0 }} animate={{ scaleX: 1 }} transition={{ delay: 0.15 + index * 0.08, duration: 0.65 }} style={{ transformOrigin: 'left' }}>
                  <Progress value={metric.value} />
                </motion.div>
              </div>
            ))}
          </div>
        )}

        <div className="grid gap-5 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <p className="eyebrow">Demonstrated / expected</p>
              <p className="font-data text-[0.65rem] text-muted-foreground">evidence map</p>
            </div>
            {skills.map((skill) => (
              <div key={skill.label} className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className={skill.priority ? 'annotation' : 'text-muted-foreground'}>{skill.label}</span>
                  <span className="font-data text-muted-foreground">{skill.value}% <span className="text-border">/</span> {skill.expected}%</span>
                </div>
                <div className="relative h-2 overflow-hidden rounded-sm bg-muted">
                  <div className="absolute inset-y-0 left-0 bg-accent-2/30" style={{ width: `${skill.expected}%` }} />
                  <motion.div initial={{ width: 0 }} animate={{ width: `${skill.value}%` }} transition={{ duration: 0.7, delay: 0.25 }} className={`relative h-full ${skill.priority ? 'bg-accent' : 'bg-accent-2'}`} />
                </div>
              </div>
            ))}
          </div>

          <div className="border-l border-border pl-5">
            <p className="eyebrow">Priority gap</p>
            <h4 className="mt-2 font-display text-3xl text-foreground">SQL</h4>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">Strong on syntax. Missing JOIN logic and normalization.</p>
            <div className="mt-4 border-t border-border pt-3">
              <p className="report-mark">Recommended next</p>
              <p className="mt-2 font-data text-xs leading-7 text-foreground">SQL Joins <span className="text-accent">→</span> Normalization <span className="text-accent">→</span> Timed Practice</p>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
