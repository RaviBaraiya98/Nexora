import { IntelligenceCore } from '@/components/intelligence/intelligence-core'
import { InterviewReport } from '@/components/intelligence/interview-report'
import { Button } from '@/components/ui/button'
import { ROUTE_PATHS } from '@/constants/route-paths'
import { usePageTitle } from '@/hooks/use-page-title'
import { motion, useMotionValueEvent, useReducedMotion, useScroll } from 'framer-motion'
import { ArrowDown, ArrowRight, Check, ChevronRight, CircleAlert, Play, Sparkles } from 'lucide-react'
import { useRef, useState } from 'react'
import { Link } from 'react-router-dom'

const companyProfiles = {
  TCS: { roles: ['Java Developer', 'Backend Engineer'], focus: 'Java collections, SQL reasoning, service fundamentals', skills: ['Java', 'OOP', 'SQL', 'DBMS', 'DSA'], difficulty: 'Intermediate' },
  Stripe: { roles: ['Software Engineer', 'Product Engineer'], focus: 'API design, distributed systems, product judgment', skills: ['APIs', 'Systems', 'SQL', 'Reliability', 'Product'], difficulty: 'Advanced' },
  Vercel: { roles: ['Frontend Engineer', 'Product Engineer'], focus: 'Web performance, JavaScript runtime, UX thinking', skills: ['React', 'JavaScript', 'Performance', 'UX', 'Systems'], difficulty: 'Advanced' },
}

const storyStages = [
  { id: 'target', label: 'Target' },
  { id: 'interview', label: 'Interview' },
  { id: 'analysis', label: 'Analysis' },
  { id: 'gap', label: 'Gap' },
  { id: 'recommendation', label: 'Next' },
  { id: 'progress', label: 'Progress' },
]

export function LandingPage() {
  usePageTitle('Career Intelligence')
  const storyRef = useRef(null)
  const prefersReducedMotion = useReducedMotion()
  const { scrollYProgress } = useScroll({ target: storyRef, offset: ['start start', 'end end'] })
  const [activeStage, setActiveStage] = useState('target')
  const [company, setCompany] = useState('TCS')
  const [role, setRole] = useState(companyProfiles.TCS.roles[0])
  const profile = companyProfiles[company]

  useMotionValueEvent(scrollYProgress, 'change', (progress) => {
    if (prefersReducedMotion) return
    const stage = storyStages[Math.min(storyStages.length - 1, Math.floor(progress * storyStages.length))]
    setActiveStage(stage.id)
  })

  function updateCompany(nextCompany) {
    setCompany(nextCompany)
    setRole(companyProfiles[nextCompany].roles[0])
  }

  return (
    <div className="relative overflow-hidden">
      <section className="mx-auto grid max-w-7xl gap-12 px-4 pb-24 pt-14 lg:grid-cols-[0.85fr_1.15fr] lg:items-center lg:px-8 lg:pt-24">
        <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.65 }} className="max-w-xl">
          <p className="eyebrow">Career intelligence / 001</p>
          <h1 className="mt-6 text-balance font-display text-5xl leading-[0.98] text-foreground md:text-7xl">Prepare with evidence. Improve with intelligence.</h1>
          <p className="mt-7 max-w-lg text-base leading-7 text-muted-foreground md:text-lg">Nexora turns company-specific interviews into a preparation loop that shows what you know, what you are missing, and what to practice next.</p>
          <div className="mt-8 flex flex-wrap items-center gap-3">
            <Link to={ROUTE_PATHS.INTERVIEW}><Button size="lg">Start your first interview <ArrowRight size={16} className="ml-2" /></Button></Link>
            <a href="#story" className="inline-flex h-12 items-center gap-2 px-3 text-sm text-muted-foreground transition-colors hover:text-foreground"><Play size={15} /> Explore the system</a>
          </div>
          <div className="mt-12 flex items-center gap-3 text-xs text-muted-foreground"><span className="h-px w-10 bg-accent" /> Company context <ChevronRight size={12} /> Interview evidence <ChevronRight size={12} /> Progress</div>
        </motion.div>
        <motion.div initial={{ opacity: 0, scale: prefersReducedMotion ? 1 : 0.98 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.7, delay: 0.1 }}><InterviewReport /></motion.div>
      </section>

      <section ref={storyRef} id="story" className="relative border-y border-border bg-background/80">
        <div className="mx-auto grid max-w-7xl gap-12 px-4 py-24 lg:grid-cols-[0.7fr_1.3fr] lg:px-8">
          <div className="lg:sticky lg:top-20 lg:h-fit">
            <p className="eyebrow">The Nexora loop</p>
            <h2 className="mt-5 max-w-md font-display text-4xl leading-tight text-foreground md:text-5xl">Preparation is everywhere. Direction isn’t.</h2>
            <p className="mt-5 max-w-md text-sm leading-7 text-muted-foreground">Every step is connected to evidence from the interview before it. No random topic lists. No empty confidence score.</p>
            <div className="mt-8"><IntelligenceCore /></div>
            <div className="mt-8 hidden space-y-2 lg:block">
              {storyStages.map((stage, index) => <button key={stage.id} onClick={() => setActiveStage(stage.id)} className={`flex w-full items-center gap-3 border-l px-3 py-2 text-left text-sm transition-colors ${activeStage === stage.id ? 'border-accent text-foreground' : 'border-border text-muted-foreground hover:text-foreground'}`}><span className="font-data text-xs">0{index + 1}</span>{stage.label}</button>)}
            </div>
          </div>

          <div className="space-y-32">
            <StoryBlock eyebrow="01 / choose your target" title="Company context turns preparation into a map.">
              <div className="grid gap-6 border border-border bg-card/70 p-5 md:grid-cols-[0.8fr_1.2fr]">
                <div className="space-y-2">{Object.keys(companyProfiles).map((name) => <button key={name} onClick={() => updateCompany(name)} className={`flex w-full items-center justify-between border-b border-border px-2 py-3 text-left text-sm ${company === name ? 'text-accent' : 'text-muted-foreground hover:text-foreground'}`}>{name}<ChevronRight size={14} /></button>)}</div>
                <div className="space-y-5">
                  <div><p className="eyebrow">Target role</p><select value={role} onChange={(event) => setRole(event.target.value)} className="mt-2 w-full border-b border-border bg-transparent py-2 font-display text-2xl text-foreground outline-none"><option className="bg-card" value={role}>{role}</option>{profile.roles.filter((item) => item !== role).map((item) => <option className="bg-card" key={item} value={item}>{item}</option>)}</select></div>
                  <div className="grid gap-4 sm:grid-cols-2"><div><p className="eyebrow">Interview focus</p><p className="mt-2 text-sm leading-6 text-muted-foreground">{profile.focus}</p></div><div><p className="eyebrow">Difficulty</p><p className="mt-2 font-data text-sm text-foreground">{profile.difficulty}</p></div></div>
                  <div className="flex flex-wrap gap-2">{profile.skills.map((skill) => <span key={skill} className="border border-border px-2 py-1 font-data text-[0.65rem] text-muted-foreground">{skill}</span>)}</div>
                </div>
              </div>
            </StoryBlock>

            <StoryBlock eyebrow="02 / the interview begins" title="A focused room for one useful question.">
              <div className="border border-border bg-card/70 p-5"><div className="flex items-center justify-between border-b border-border pb-4"><span className="eyebrow">{company} · {role}</span><span className="font-data text-xs text-accent">08:42</span></div><p className="mt-8 max-w-2xl font-display text-3xl leading-tight text-foreground">Explain the difference between HashMap and ConcurrentHashMap.</p><div className="mt-8 border-l-2 border-accent px-4 py-3 text-sm leading-7 text-muted-foreground">“I would use HashMap because it gives constant-time lookup and is useful for key-value access...”</div><div className="mt-8 flex items-center justify-between text-xs text-muted-foreground"><span>Question 03 of 08</span><span className="font-data">Technical / Java</span></div></div>
            </StoryBlock>

            <StoryBlock eyebrow="03 / answer becomes intelligence" title="Analysis makes the invisible parts of an answer legible."><InterviewReport compact activeStage="analysis" /></StoryBlock>

            <StoryBlock eyebrow="04 / find the gap" title="The insight is the distance between expected and demonstrated.">
              <div className="border border-border bg-card/70 p-5"><div className="mb-5 flex items-center justify-between"><span className="eyebrow">Role requirement / evidence</span><span className="annotation">priority signal</span></div>{[['Java', 90, 86], ['OOP', 88, 80], ['DSA', 80, 68], ['SQL', 75, 32], ['DBMS', 72, 55]].map(([name, expected, demonstrated]) => <div key={name} className="mb-5 grid grid-cols-[70px_1fr_65px] items-center gap-3 text-xs"><span className={name === 'SQL' ? 'annotation' : 'text-muted-foreground'}>{name}</span><div className="relative h-5 border-y border-border"><div className="absolute top-1/2 h-px -translate-y-1/2 bg-accent-2/40" style={{ width: `${expected}%` }} /><motion.div initial={{ width: 0 }} whileInView={{ width: `${demonstrated}%` }} viewport={{ once: true }} transition={{ duration: 0.7 }} className={`absolute top-1/2 h-1 -translate-y-1/2 ${name === 'SQL' ? 'bg-accent' : 'bg-accent-2'}`} /></div><span className="font-data text-right text-muted-foreground">{demonstrated}%</span></div>)}<p className="border-t border-border pt-4 text-sm leading-6 text-muted-foreground"><CircleAlert size={15} className="mr-2 inline text-accent" />SQL is not a verdict. It is the next useful question.</p></div>
            </StoryBlock>

            <StoryBlock eyebrow="05 / recommendation" title="The next action is a consequence, not a guess.">
              <div className="border border-accent/40 bg-accent/5 p-5"><div className="flex items-center gap-3"><Sparkles size={16} className="text-accent" /><p className="eyebrow text-accent">Nexora recommendation path</p></div><div className="mt-8 flex flex-col gap-3 font-data text-sm text-foreground md:flex-row md:items-center"><span className="border border-border bg-card px-3 py-3">SQL Joins</span><ArrowRight className="text-accent" size={16} /><span className="border border-border bg-card px-3 py-3">Normalization</span><ArrowRight className="text-accent" size={16} /><span className="border border-accent bg-accent px-3 py-3 text-accent-foreground">Timed SQL Set</span></div></div>
            </StoryBlock>

            <StoryBlock eyebrow="06 / return stronger" title="Practice becomes visible when the loop remembers.">
              <div className="border border-border bg-card/70 p-5"><div className="grid gap-4 md:grid-cols-3">{[['Attempt 01', '32%', 'SQL weak'], ['Attempt 02', '51%', 'Joins clearer'], ['Attempt 03', '68%', 'Normalization next']].map(([attempt, score, note], index) => <div key={attempt} className="relative border-l border-border pl-4"><span className="eyebrow">{attempt}</span><p className="mt-3 font-data text-3xl text-foreground">{score}</p><p className="mt-2 text-xs text-muted-foreground">{note}</p>{index < 2 && <ArrowRight className="absolute -right-3 top-8 hidden bg-card text-accent md:block" size={18} />}</div>)}</div><div className="mt-8 data-line" /><p className="mt-4 flex items-center gap-2 text-sm text-positive"><Check size={15} /> Improvement becomes a practice history, not a feeling.</p></div>
            </StoryBlock>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-4xl px-4 py-28 text-center lg:px-8"><p className="eyebrow">Start with the next question</p><h2 className="mt-5 font-display text-5xl leading-tight text-foreground md:text-7xl">Stop guessing what to prepare. Know what to improve next.</h2><Link to={ROUTE_PATHS.INTERVIEW} className="mt-8 inline-block"><Button size="lg">Start your first interview <ArrowRight size={16} className="ml-2" /></Button></Link><div className="mt-12 flex justify-center text-muted-foreground"><ArrowDown size={18} /></div></section>
    </div>
  )
}

function StoryBlock({ eyebrow, title, children }) {
  return <motion.section initial={{ opacity: 0, y: 22 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, amount: 0.2 }} transition={{ duration: 0.55 }}><p className="eyebrow">{eyebrow}</p><h3 className="mt-4 max-w-2xl font-display text-3xl leading-tight text-foreground md:text-4xl">{title}</h3><div className="mt-7">{children}</div></motion.section>
}
