import { StatCard } from '@/components/common/stat-card'
import { InterviewReport } from '@/components/intelligence/interview-report'
import { TopNav } from '@/components/layout/top-nav'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { usePageTitle } from '@/hooks/use-page-title'
import { interviewService } from '@/services/interview-service'
import { motion } from 'framer-motion'
import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

export function DashboardPage() {
  usePageTitle('Dashboard')
  const [interviews, setInterviews] = useState([])
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([interviewService.list(), interviewService.reports()])
      .then(([interviewResponse, reportResponse]) => {
        setInterviews(interviewResponse.interviews || [])
        setReports(reportResponse.reports || [])
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const readiness = useMemo(() => {
    const values = reports.map((report) => report.analysis?.technical_relevance).filter(Number.isFinite)
    return values.length ? Math.round(values.reduce((sum, value) => sum + value, 0) / values.length) : null
  }, [reports])

  const progress = useMemo(() => reports.map((report, index) => ({ attempt: `#${index + 1}`, score: report.analysis?.technical_relevance || 0 })), [reports])
  const roles = new Set(interviews.map((item) => item.role).filter(Boolean))

  return (
    <div>
      <TopNav title="Readiness Command Center" subtitle="Your saved preparation signals" />
      <div className="mb-6 grid gap-6 xl:grid-cols-[1.15fr_0.85fr] xl:items-start">
        <div><p className="eyebrow">Personal preparation record</p><h2 className="mt-3 max-w-2xl font-display text-4xl leading-tight text-foreground">Your preparation has a direction.</h2><p className="mt-3 max-w-xl text-sm leading-6 text-muted-foreground">{reports.length ? 'Your readiness is calculated from your saved interview reports.' : 'Complete your first interview to create your readiness record.'}</p></div>
        {reports.length ? <InterviewReport compact /> : <div className="border border-dashed border-border p-5 text-sm text-muted-foreground">Your interview report will appear here after analysis.</div>}
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Readiness Score" value={readiness ?? '—'} suffix={readiness ? '%' : ''} delta={readiness ? 'From saved reports' : 'Awaiting first interview'} />
        <StatCard label="Interviews Completed" value={interviews.length} delta="Saved to your account" />
        <StatCard label="Target Roles Mapped" value={roles.size} delta="From interview history" />
        <StatCard label="AI Reports" value={reports.length} delta="Generated for your account" />
      </div>

      <div className="mt-6 grid gap-4 xl:grid-cols-3">
        <Card className="xl:col-span-2">
          <CardHeader><CardTitle>Personal Readiness Progress</CardTitle></CardHeader>
          <CardContent className="h-72">
            {progress.length ? <ResponsiveContainer width="100%" height="100%"><LineChart data={progress}><XAxis dataKey="attempt" stroke="var(--muted-foreground)" /><YAxis stroke="var(--muted-foreground)" domain={[0, 100]} /><Tooltip /><Line type="monotone" dataKey="score" stroke="var(--accent)" strokeWidth={2.5} /></LineChart></ResponsiveContainer> : <div className="flex h-full items-center justify-center text-sm text-muted-foreground">Complete interviews to see your progress.</div>}
          </CardContent>
        </Card>
        <Card><CardHeader><CardTitle>Account Insight</CardTitle></CardHeader><CardContent className="space-y-3 text-sm text-muted-foreground">{loading ? <p>Loading saved data...</p> : reports.length ? <p>Open Reports to review the evidence and recommendations generated from your interviews.</p> : <p>Your first completed interview will generate personalized insight here.</p>}</CardContent></Card>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Card><CardHeader><CardTitle>Recent Interviews</CardTitle></CardHeader><CardContent className="space-y-3">{interviews.map((item) => <Link key={item._id || `${item.company}-${item.createdAt}`} to={`/interview/${item._id}`}><motion.div whileHover={{ x: 2 }} className="rounded-xl border border-border bg-muted/40 p-3"><div className="flex items-center justify-between"><div><p className="font-medium text-foreground">{item.companySnapshot?.name}</p><p className="text-xs text-muted-foreground">{item.roleSnapshot?.name}</p></div><Badge>{item.status || 'saved'}</Badge></div><p className="mt-2 text-xs text-muted-foreground">{item.createdAt ? new Date(item.createdAt).toLocaleDateString() : 'Saved interview'}</p></motion.div></Link>)}{!interviews.length && !loading ? <p className="text-sm text-muted-foreground">No interviews saved yet.</p> : null}</CardContent></Card>
        <Card><CardHeader><CardTitle>Next Action</CardTitle></CardHeader><CardContent className="space-y-3 text-sm text-muted-foreground"><p>{reports.length ? 'Review your latest report and choose its recommended practice topic.' : 'Start an interview to create your first report.'}</p><Badge>{reports.length ? 'Report review' : 'Interview needed'}</Badge></CardContent></Card>
      </div>
    </div>
  )
}
